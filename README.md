## Certified Operators Migration Step by Step

    REQUIRED MANUAL STEPS BEFORE RUNNING THIS
    1. Login access.redhat.com/user with your masquared account 
    2. Create a new certification project of type 'operator bundle image'
    3. remove package-lock or ask someone to do it for the migrating operator
  </br>

    Software Requirements:
    - offline-cataloger -> https://github.com/kevinrizza/offline-cataloger
    - operator-courier -> https://github.com/operator-framework/operator-courier
    - opm -> https://github.com/operator-framework/operator-registry/releases

#### Prepare the environment:

1) Clone the project and cd into it:
```
git clone git@github.com:acmenezes/bundle-migration.git
cd bundle-migration
```

2) Pull the certified operators manifests to your local machine:
```
make pull-cert-operators
```

3) Configure the Makefile for the operator being migrated:

```
BUILDER= <---- You may use docker or podman
OPERATOR_NAME= <----- that should be the name in the outermost folder Ex: portworx-certified
BUNDLE_DIR= <----- the whole path for the nested bundle from the root of this project like below

        BUNDLE_DIR=manifests-435264820/portworx-certified/portworx-certified-5edb2jey

PUSH_REGISTRY= <--- you may use quay as a first registry for testing here

For production it should be like below:
PUSH_REGISTRY=scan.connect.redhat.com

PROJECT_ID= <--- retrieved from the new project id in connect.redhat.com with the masquarade account
```
---

#### If you want to test/run everything at once run:

For nested directories:
```
make all
```

For flat directories:
```
make all FLAT=true
```

---

#### If you want to go step by step follow the steps below:

1) If the operator has a flat directory:

Then run:
```
$ make nest FLAT=true
```
Remark that the new one will have the old name and the old one will have `-flat-old` appended.

2) Run the migrate command that will generate the dockerfiles to build and push the images:
```
make migrate-bundle
```
This last one runs opm under the hood and [here](docs/opm_alpha_generate.md) you can find what opm is doing.

3) Build all images for each version of the current operator:
```
make build-bundle-images
```

4) Tag those images with the PUSH_REGISTRY configured (may be a test one or the final one):
```
make tag-bundle-images
```

5) Push the images tagged on the last step

```
If versions are to be pushed individually just do:

$ podman or docker images on local machine and pick the right version, then
$ podman or docker push with format ${PUSH_REGISTRY}/${PROJECT_ID}:$$operator_tag;

replacing PUSH_REGISTRY and PROJECT_ID accordingly.

make push-bundle-images is commented out but may be used if needed to push in bulk
```
