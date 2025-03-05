from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data=None, accepted_media_type=None, renderer_context=None, *args, **kwargs):
        response = renderer_context.get('response', None)

        # Handle errors from exception responses
        if response and response.status_code >= 400:
            if isinstance(data, dict):
                error_message: str = data.get("detail")

                if not error_message and isinstance(data, dict):
                    error_message = str(list(data.items())) if data else "An error occurred!"

                response_data = {
                    "status": response.status_code,
                    "message": error_message
                }

            else:
                response_data = {
                    "status": response.status_code,
                    "message": data[0] if data else None
                }

        else:
            # Standard success response
            response_data = {
                'status': response.status_code,
                'message': '',
                'data': data
            }

        return super().render(response_data, *args, **kwargs)