import string
import random
import functools


def random_str():
    return ''.join(random.choices(string.ascii_uppercase +
                                  string.digits, k=8))
# stream_recorder({'uri' : url, 'uuid': uuid})

# thread = threading.Thread(target=stream_recorder, args=(url, uuid))
# thread.start()
# threads.append((thread, uuid))


def validate_serializer(serializer):
    """
    @validate_serializer(TestSerializer)
    def post(self, request):
        return self.success(request.data)
    """
    def validate(view_method):
        @functools.wraps(view_method)
        def handle(*args, **kwargs):
            self = args[0]
            request = args[1]
            s = serializer(data=request.data)
            if s.is_valid():
                request.data = s.data
                request.serializer = s
                return view_method(*args, **kwargs)
            else:
                return self.invalid_serializer(s)

        return handle

    return validate
