from typing import Callable
import json
from pandas import DataFrame, concat

import urllib.request
import requests

from flask import render_template, Flask
from flask import request

from siminfo import BASE_URLS, PARAMS, fake_request_function

app = Flask(__name__)

class Coalesce:
    """
    Coalesce several API plan information values and render

    Attributes
    ----------
    base_urls : set
        Set of urls that are to be queried for plan information

    Methods
    -------
    coalesce_plan_info(member_id, request_function, modewt, medianwt)
        Query the base_urls using the request function and coalesce the values
    requests_adapter(url)
        An adapter that queries urls using the requests library
    urllib_adapter(url)
        An adapter that queries urls using the urllib library
    """
    def __init__(self, base_urls = BASE_URLS):
        """
        Parameters
        ----------
        base_urls : set
            set of API url strings to query for plan information
        """
        self.base_urls = base_urls.copy()

    def coalesce_plan_info(self, member_id, request_function: Callable,
                           modewt=0., medianwt=0.) -> dict:
        """
        Parameters
        ----------
        member_id : int
            specific member id to query for and coalesce
        request_function : Callable
            adapter for processing the API URL
        modewt : float
            the weight of mode the deductible, stop_loss and oop_max
        medianwt : float
            the weight of median of the deductible, stop_loss and oop_max

        Returns
        -------
        dict
            for deductible, stop_loss and oop_max, the coalesced values
            or "no data" if unable to acquire any values
        """
        plan_infos = DataFrame()
        for base_url in self.base_urls:
            url = base_url+PARAMS.format(member_id=member_id)
            try:
                request_result = request_function(url)
            except:
                print(f"skipping failed request from {url}")
                continue
            result = DataFrame(request_result, index=[url])
            plan_infos = concat([plan_infos, result])

        meanwt = 1.-modewt-medianwt
        # can also have config e.g. by column
        # (.5*max(deductible)+.5*min(deductible), 
        # min(stop_loss),...) etc; omitted for clarity
        weighted_result = (meanwt*plan_infos.mean()+
            medianwt*plan_infos.median()+
            modewt*plan_infos.mode()).astype(int)

        if weighted_result.shape[0] == 0:
            return({k: "no data" for k in
                ["deductible","stop_loss","oop_max"]})
        return weighted_result.loc[0].to_dict()

    @classmethod
    def requests_adapter(url: str) -> dict:
        """
        An adapter that encapsulates requests.get
        Parameters
        ----------
        url : str
            the API url to call to acquire data

        Returns
        -------
        dict
            converts json response of plan information to dict
        """
        resp = requests.get(url, timeout=10)
        return resp.json()


    @classmethod
    def urllib_adapter(url: str) -> dict:
        """
        An adapter that encapsulates urllib.urlopen
        Parameters
        ----------
        url : str
            the API url to call to acquire data

        Returns
        -------
        dict
            converts json response of plan information to dict
        """
        with urllib.request.urlopen(url, timeout=10) as response:
            resp = response.read()
        return json.loads(resp)

@app.route("/")
@app.route("/index")
def index():
    """
    Given memberid, modewt and medianwt as URL query parameters, 
    display coalesced plan info
    Returns
    -------
        rendered template for Flask to display
    """

    member_id = request.args.get("member_id", type=int)
    modewt = request.args.get("modewt", type=float, default=0.)
    medianwt = request.args.get("medianwt", type=float, default=0.)
    c = Coalesce(BASE_URLS)
    plan_info = c.coalesce_plan_info(member_id, 
            request_function=fake_request_function,
            modewt=modewt, medianwt=medianwt)

    return render_template("index.html", 
            member_id=member_id, 
            plan_info=plan_info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
