FROM scratch

LABEL operators.operatorframework.io.bundle.mediatype.v1=registry+v1
LABEL operators.operatorframework.io.bundle.manifests.v1=manifests/
LABEL operators.operatorframework.io.bundle.metadata.v1=metadata/
LABEL operators.operatorframework.io.bundle.package.v1=couchdb-operator-certified
LABEL operators.operatorframework.io.bundle.channels.v1=v1.2
LABEL operators.operatorframework.io.bundle.channel.default.v1=v1.2

COPY migration_artifacts/couchdb-operator-certified/1.2.1/manifests /manifests/
COPY migration_artifacts/couchdb-operator-certified/1.2.1/metadata /metadata/
LABEL com.redhat.openshift.versions=v4.6,v4.5
LABEL com.redhat.delivery.operator.bundle=true
LABEL com.redhat.delivery.backport=true