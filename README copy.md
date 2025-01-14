# zivid @nova

Zivid integration for Wandelbots Nova

## install

* requirement: [nova cli](https://github.com/wandelbotsgmbh/wabocli)

```bash
# currently only machines with some intel gpu (integrated gpu will also work) are supported
$ nova catalog install zivid-intel
```

## rerun.io support

This service can log contents to a rerun.io instance. In order to do that one needs to provide `RERUN_ADDR` in format `hostname:port` or `ip:port`.
**Note** If the pointcloud is not downsampled, it will slow down the viewer.

It is expected, that rerun.io is deployed independent from this service. For this you can have a look here: https://code.wabo.run/ai/rerun-nova
`rerunAddress` in the helm values yaml must be set and zivid must be deployed with helm (not via catalog) or skaffold.

Helm:
```bash
# add the repo
$ helm repo add zivid-nova https://code.wabo.run/api/v4/projects/650/packages/helm/release

# install zivid with rerun enabled
$ helm upgrade -i --create-namespace -n zivid zivid-nova zivid-nova/zivid-nova --set rerunAddress=rerun.rerun.svc.cluster.local:9876

# uninstall
$ helm uninstall zivid-nova -n zivid
```

Skaffold:
```bash
$ skaffold run
```

## development

* the zivid http service can also be installed by [skaffold](https://skaffold.dev/)
    * `skaffold dev --cleanup=false --status-check=false`

### formatting

* `poetry run black zivid_nova`
* `poetry run isort zivid_nova tests`

## further reading

For more in depth device integration information you can have a look in the [docs for the initial integration](docs/oldreadme.md)