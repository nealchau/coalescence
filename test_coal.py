from coal import Coalesce, app
from pandas import DataFrame
from http import HTTPStatus
import pytest

from siminfo import BASE_URLS, API_RESPONSES, fake_request_function

@pytest.fixture(scope="module")
def client():
    """creates client connection to flask for testing_client"""

    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()

class FakeCorrectResult:
    """
    Methods
    -------
    calc : dict
        a dictionary of the correct plan information
        weighted result
    """

    def calc(self, modewt=0., medianwt=0.):
        """
        calculate weighted plan information

        Parameters
        ----------
        modewt : float
            the weight of mode the deductible, stop_loss and oop_max
        medianwt : float
            the weight of median of the deductible, stop_loss and oop_max

        Returns
        -------
        dict
            for deductible, stop_loss and oop_max, the coalesced values
        """
        meanwt = 1.-modewt-medianwt

        weighted_result = (meanwt*API_RESPONSES.mean()+
            medianwt*API_RESPONSES.median()+
            modewt*API_RESPONSES.mode()).astype(int)

        return(weighted_result.loc[0].to_dict())

# Only test the API coalesce_plan_info function

def test_default_mean():
    """default coalesence is mean"""
    c = Coalesce(BASE_URLS)
    output = c.coalesce_plan_info(1, fake_request_function)
    assert output == FakeCorrectResult().calc()

def test_median():
    """check median weighting"""
    c = Coalesce(BASE_URLS)
    output = c.coalesce_plan_info(1, fake_request_function, 
            modewt=0, medianwt=1)
    assert output == FakeCorrectResult().calc(modewt=0, medianwt=1)

def test_mode():
    """check mode weighting"""
    c = Coalesce(BASE_URLS)
    output = c.coalesce_plan_info(1, fake_request_function, 
            modewt=1, medianwt=0)
    print(output)
    assert output == FakeCorrectResult().calc(modewt=1, medianwt=0)

def test_badurls():
    """
    if some APIs are unavailable, we should skip them
    and return the result based on those that are responsive
    """

    badurls = BASE_URLS.copy()
    badurls.add("unavailable.url.com")
    c = Coalesce(base_urls=badurls)
    output = c.coalesce_plan_info(1, fake_request_function)
    assert output == FakeCorrectResult().calc()

# Test the API and the Flask rendered page

def test_mean_client(client):
    """
    through client check mean rendering

    Parameters
    ----------
    client : flask client
        testing client setup by pytest fixture
    """
    resp = client.get("/?member_id=1")
    assert resp.status_code == HTTPStatus.OK
    assert b"Deductible: 1066" in resp.data
    assert b"Stop Loss: 11000" in resp.data
    assert b"OOP Max: 5666" in resp.data

def test_median_mode(client):
    """
    through client check .5 median+.5 mode rendering

    Parameters
    ----------
    client : flask client
        testing client setup by pytest fixture

    """
    resp = client.get("/?member_id=1&medianwt=.5&modewt=.5")
    assert resp.status_code == HTTPStatus.OK
    assert b"Deductible: 1000" in resp.data
    assert b"Stop Loss: 10000" in resp.data
    assert b"OOP Max: 6000" in resp.data

def test_missing_member_id(client):
    """
    if a member has no data, show appropriate message

    Parameters
    ----------
    client : flask client
        testing client setup by pytest fixture
    """
    resp = client.get("/?member_id=2")
    assert resp.status_code == HTTPStatus.OK
    assert b"Deductible: no data" in resp.data
    assert b"Stop Loss: no data" in resp.data
    assert b"OOP Max: no data" in resp.data


def test_missing_member_id(client):
    """
    for malformed query show appropriate message

    Parameters
    ----------
    client : flask client
        testing client setup by pytest fixture
    """


    resp = client.get("/?badquery=2")
    assert resp.status_code == HTTPStatus.OK
    assert b"Deductible: no data" in resp.data
    assert b"Stop Loss: no data" in resp.data
    assert b"OOP Max: no data" in resp.data

