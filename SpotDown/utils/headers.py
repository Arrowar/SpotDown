# 05.04.2024


# External library
import ua_generator


# Variable
ua =  ua_generator.generate(device='desktop', browser=('chrome', 'edge'))


def get_userAgent() -> str:
    return ua_generator.generate(device='desktop', browser=('chrome', 'edge')).text



def get_headers() -> dict:
    return ua.headers.get()