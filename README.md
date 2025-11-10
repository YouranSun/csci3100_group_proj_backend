## How to run

1. Clone this repo. (Remember to turn on the VPN to access OPENAI api)

```sh
pip install -r requirements.txt
```

2. Create an example in `example/`

    * Create `example/main.py`

        ```py
        print("Hello world!")
        ```

    * Create a git repository in `example`

        ```sh
        cd ./example
        git init
        ```

    * Make initial commit

        ```sh
        git commit -m "inital commit"
        ```

    * Make a change to this `main.py`

        ```py
        print("Hello world!")
        print("What do you want to do?")
        ```

    * Stage the change

        ```sh
        git add .
        ```

3. Test the functions

    ```sh
    cd ..
    python main.py
    ```

## Notes

1. Please do not use the API key for other purposes.

## To-dos

1. When uploading repos, check conflict with existing repos

2. The color of unselected repos