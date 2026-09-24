from mvp_api.auth import create_token

if __name__ == "__main__":
    print(create_token("enterprise-demo", 1000000))
