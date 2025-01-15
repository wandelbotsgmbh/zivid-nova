# zivid-nova

[Zivid](https://www.zivid.com/de/) integration for Wandelbots Nova

## install

* requirement: [nova cli](https://github.com/wandelbotsgmbh/wabocli)

```bash
# Currently only machines with intel gpu (integrated gpu will also work) are supported with Nova.
# Nvidia GPU support is in preparation.
$ nova catalog install zivid-intel
```

## api

The first draft of the spec can be seen here [openapi.json](openapi.json).

## development

### formatting

* `poetry run black zivid_nova`
* `poetry run isort zivid_nova tests`

### running locally

* make sure [Zivid SDK](https://support.zivid.com/en/latest/index.html) is installed on your machine 
* install project dependencies `poetry install`
* run the project with `poetry run serve`
    * if your are using vscode you can press F5
* visit `127.0.0.1:8080` to access the [api docs](openapi.json)
