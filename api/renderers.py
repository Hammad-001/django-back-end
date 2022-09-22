from rest_framework.renderers import JSONRenderer
import json


class UserRenderer(JSONRenderer):
    # to show errors in frontend creating a custom json renderer
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ""
        if "ErrorDetail" in str(data):
            response = json.dumps({"errors": data})
        else:
            response = json.dumps(data)
        return response
