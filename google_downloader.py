import time
import requests

def download_file_from_google_drive(id, destination, f_size=None):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination, f_size=None):
        CHUNK_SIZE = 32768
        n_rate = -1
        o_rate =  0
        n_recv =  0
        o_time = int(time.time())
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    n_recv += CHUNK_SIZE
                    if f_size != None:
                        o_rate = "%0.0f" % (float(n_recv)/float(f_size) * 100.00)
                        #print("n_recv=%d, f_size=%d, o_rate=%s" % (n_recv, f_size, o_rate))
                        if n_rate != o_rate or o_time != int(time.time()):
                            o_rate2 = "%0.2f" % (float(n_recv)/float(f_size) * 100.00)
                            print("file=%s downloading... %s%% completed" % (destination, o_rate2))
                            o_time = int(time.time())
                        n_rate = o_rate
                    f.write(chunk)

    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination, f_size)    


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python google_drive.py drive_file_id destination_file_path")
    else:
        # TAKE ID FROM SHAREABLE LINK
        file_id = sys.argv[1]
        # DESTINATION FILE ON YOUR DISK
        destination = sys.argv[2]
        f_size = None
        if len(sys.argv) >= 4:
            f_size = int(sys.argv[3])

        download_file_from_google_drive(file_id, destination, f_size)
