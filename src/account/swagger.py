from drf_yasg.openapi import Schema


def sample_employer_account_request_schema():
    return Schema(
        type='object',
        properties={
            'email': Schema(type='string', default='username@sample.com'),
            'username': Schema(type='string', default='username'),
            'last_name': Schema(type='string', default='Snow'),
            'first_name': Schema(type='string', default='Jon'),
            'password': Schema(type='string', default='password'),
            'phone_number': Schema(type='string', default='+48123456789'),
            'nip': Schema(type='string'),
            'company_name': Schema(type='string'),
            'company_address': sample_address_schema(),
        },
        required=['email', 'username', 'password', 'last_name', 'first_name', 'phone_number', 'nip', 'company_name',
                  'company_address']
    )


def sample_default_account_request_schema():
    return Schema(
        type='object',
        properties={
            'email': Schema(type='string', default='username@sample.com'),
            'username': Schema(type='string', default='username'),
            'last_name': Schema(type='string', default='Snow'),
            'first_name': Schema(type='string', default='Jon'),
            'password': Schema(type='string', default='password'),
            'phone_number': Schema(type='string', default='+48123456789'),
            'facility_name': Schema(type='string'),
            'facility_address': sample_address_schema(),
        },
        required=['email', 'username', 'password', 'last_name', 'first_name', 'phone_number', 'facility_name',
                  'facility_address']
    )


def sample_address_schema():
    return Schema(
        type='object',
        properties={
            'city': Schema(type='string', default='Warszawa'),
            'street': Schema(type='string', default='Miodowa'),
            'street_number': Schema(type='integer', default='1'),
            'postal_code': Schema(type='string', default='00-000')
        },
        required=['city', 'street', 'street_number', 'postal_code']
    )


def sample_login_response(account_type):
    response = Schema(properties={
        'expiry': Schema(type='string', default='2020-05-14T08:10:46.354741+02:00'),
        'token': Schema(type='string', default='e9127a24c2e1300acb0afd8f4776343c59f2b9450369317086f421ce6c897ed6'),
        'type': Schema(type='string', default=account_type)
    },
        type='object'
    )
    return response
