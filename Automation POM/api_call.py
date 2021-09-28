import requests

from credentials import Credentials
API_TOKEN = Credentials.API_PERSONAL_TOKEN_ASANA


class ApiCall:
    def __init__(self, API_TOKEN, base_url) -> dict:
        """
        :param `API_TOKEN`: The (string) value of the api token
        :param `base_url`: The (string) value of the url 
            Ex: https://app.asana.com/api/1.0/
        :param `route`: The (string) value of the base route to be appended to base_url
            Ex: `projects`
        :param `*args`: The variable (strings) of any additional data objects to be added, including ids
            Ex: https://app.asana.com/api/1.0/projects/{project_gid}/addCustomFieldSetting
                with `{project_gid}` being an actual id and `addCustomFieldSetting` being the required route
        :param `**kwargs`: The (string) value of additional parameters to specify a query usually comes after a `?`
            Ex: `opt_pretty=True` which will be sent as https://app.asana.com/api/1.0/projects?opt_pretty=True
        """
        self.API_TOKEN = API_TOKEN
        self.base_url = base_url

    def route(self, route, *args, **kwargs):

        print(f'{self.base_url}{route}/{args[0]}/{args[1]}')
        API_TOKEN
        with requests.Session() as self.session:
            
            projects = self.session.get('https://app.asana.com/api/1.0/projects?opt_pretty=True', auth=(API_TOKEN, ''))
            test = self.session.get(f'{self.base_url}{route}/{args[0]}/{args[1]}', auth=(API_TOKEN, ''), timeout=2.5)
        print(test.status_code, test.text)

    
       
henry = ApiCall(API_TOKEN, 'https://app.asana.com/api/1.0/', 'projects', '1199214815233072','tasks')
