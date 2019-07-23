# Merakisight

A Webex Teams bot that combines the power of Meraki and Intersight to provide infrastructure-wide health monitoring


## Business/Technical Challenge

The idea for *Merakisight* initially began from our experiences and successes with the Intersight and Meraki dashboards. We've seen that Cisco has been moving rapidly toward consolidation of its offerings into cloud-based platforms. However, the benefits of these tools are still segmented by their individual platforms. This means that customers who are bought in to the Cisco vision of single pane of glass management for all their Cisco products still have to login to each portal individually in order to get an insight into the overall health of their environment.


## Proposed Solution

*Merakisight* is a solution that further extends Cisco's vision for unified cloud-based visibility and the benefits that customers gain by going all-in with Cisco! We accomplish this by providing a Webex Teams bot that has access to both their cloud-based management portals. This bot provides a unified overall concept of "health" and displays it in regularly scheduled messages. These messages are configurable per the user's desired timings and thresholds. In the event that the health of the environment is below the configured threshold, quick access links into Meraki and/or Intersight will be provided for agile troubleshooting.  


## Cisco Products Technologies/ Services

Our solution will levegerage the following Cisco technologies:

* [Meraki Dashboard](https://meraki.cisco.com/)
* [Intersight](https://intersight.com/)
* [Webex Teams](https://www.webex.com/team-collaboration.html)

## Team Members

* Bradford Ingersoll (<bingerso@cisco.com>) - GVS Data Center
* Eric Scott (<eriscott@cisco.com>) - GVS US Public Sector


## Solution Components

Our solution utilizes the following components:

### Code
* [Python 3.7.3](https://www.python.org/) - Foundational programming language for Merakisight
    * [webexteamsbot](https://github.com/hpreston/webexteamsbot/tree/master/webexteamsbot) - Python module to facilitate bot functionality
    * [meraki_module](https://github.com/meraki/dashboard-api-python) - Python module to facilitate integration with Meraki's API
    * [intersight_auth](https://github.com/movinalot/intersight-rest-api/blob/master/intersight_auth.py) - Python module to facilitate authentication for Intersight API
    * [requests](https://2.python-requests.org/en/master/) - Python module to perform all other API requests

### API's Used
* [Meraki Dashboard](https://developer.cisco.com/meraki/api/)
    * [GET Organization Device Statuses](https://developer.cisco.com/meraki/api/#/rest/api-endpoints/organizations/get-organization-device-statuses) - Returns status of all devices to be used in health calculation (online devices / total devices)
    * [GET Network Connection Stats](https://developer.cisco.com/meraki/api/#/rest/api-endpoints/wireless-health/get-network-connection-stats) - Returns status of all wireless client connection attempts to be used in health calculation (successful connections / total connections) 
* [Intersight](https://intersight.com/apidocs/introduction/overview/)
    * [GET computePhysicalSummary](https://intersight.com/apidocs/compute/PhysicalSummaries/get/) - Returns operStatus of all compute devices to be used in health calculation (devices with ok operStatus / total devices)

### Hosting (OPTIONAL)
* [pythonanywhere](https://www.pythonanywhere.com) - Bot hosting (not required for local deployment)


## Usage

Once deployed, add the Merakisight bot to a space in Webex Teams.
Interact with Merakisight using the provided commands:
* **/help**: List all commands available.
* **/changefrequency [daily/hourly]**: Set the frequency (hourly or daily) for Merakisight reporting
* **/startmonitoring**: Tell Merakisight to start monitoring at the configured interval
* **/stopmonitoring**: Tell Merakisight to stop monitoring
* **/healthcheck**: Run a health check right now


## Installation

*For local deployments, use something like [ngrok](https://ngrok.com/) to enable Webex Teams webhook.*

0. Install [Python (3.6+)](https://www.python.org/downloads/)
1. Clone this repository
```
git clone https://github.com/totallybradical/fy19q4-asic-merakisight.git
```
2. Create a virtual environment
```
python3.6 -m venv venv
source venv/bin/activate
```
3. Install the required python modules
```
pip install -r requirements.txt
```
4. Set required environment variables
```
export TEAMS_BOT_APP_NAME=<BOT_APP_NAME>
export TEAMS_BOT_EMAIL=<BOT_EMAIL>
export TEAMS_BOT_URL=<BOT_URL>
export MERAKI_API_KEY=<MERAKI_API_KEY>
export INTERSIGHT_API_KEY=<INTERSIGHT_API_KEY>
export TEAMS_BOT_TOKEN=<BOT_TOKEN>
export PYTHONANYWHERE_API_KEY=<PA_TOKEN>
export MERAKI_ORG_ID=<MERAKI_ORG_ID>
export MERAKI_NETWORK_ID=<MERAKI_NETWORK_ID>
```
5. Start the bot (and leave it running)
```
python merakisight.py
```


## Documentation

*Links to relevant documentation are included throughout the README*


## License

Provided under Cisco Sample Code License, for details see [LICENSE](./LICENSE.md)

## Code of Conduct

Our code of conduct is available [here](./CODE_OF_CONDUCT.md)

## Contributing

See our contributing guidelines [here](./CONTRIBUTING.md)
