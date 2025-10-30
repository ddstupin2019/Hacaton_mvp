import openai



def get_promt():
    with open('promt.txt') as f:
        return f.read()

def get_res(path, path_out):
    YANDEX_CLOUD_MODEL = ""
    YANDEX_CLOUD_API_KEY = ''
    YANDEX_CLOUD_FOLDER = ''

    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project=YANDEX_CLOUD_FOLDER
    )
    text = ''
    with open(path) as f:
        text = f.read()

    zapr = get_promt() + '\n' + text

    r_text = '''
    response = client.responses.create(
        model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
        input=zapr,
        temperature=0.2,
        max_output_tokens=1000
    )

    r_text = str(response.output[0].content[0].text)
    '''
    with open(path_out, 'w', encoding='utf-8') as f:
        f.write(r_text)

    print('end model')
