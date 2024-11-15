import boto3
from botocore.exceptions import ClientError

def send_email(subject_text, body_html_text, from_email, to_emails, to_bcc_emails):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = from_email

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENTS = to_emails
    BCC_RECIPIENTS = to_bcc_emails

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "Default"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "ap-northeast-2"

    # The subject line for the email.
    SUBJECT = subject_text

    # The HTML body of the email.
    BODY_HTML = body_html_text

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses':
                    RECIPIENTS,
                'BccAddresses':
                    BCC_RECIPIENTS
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
        # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

if __name__ == '__main__':
    subject_text = "안녕하세요"
    from_email = "Info <info@inter-stay.com>"
    to_email = "soowoomi@gmail.com"
    body_html_text = """<html>
    <head></head>
    <body>
    <h1>Amazon SES Test (SDK for Python)</h1>
    <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>
            """

    send_email(subject_text, body_html_text, from_email, to_email)