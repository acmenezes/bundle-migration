#! /usr/bin/env python3

import yaml
import subprocess
import os
import shutil

class BundleMigration:
  def __init__(self):
    
    # loading options
    with open("migrate.yaml") as m:
      self.options = yaml.load(m, Loader=yaml.FullLoader)

    # loading operator list
    self.operators = []
    [self.operators.append(operator) for operator in self.options]

    # loding input path
    self.manifests_path = []
    [self.manifests_path.append(d) for d in os.listdir('.') if d.startswith('manifests-')]    
    if not self.manifests_path:
      self.download_manifests()

  def update_manifests(self):
    self.delete_old_manifests()
    self.download_manifests()
    self.delete_unused_bundles()
    self.nest_flat_operators()

  def delete_old_manifests(self):
     [shutil.rmtree(path) for path in self.manifests_path]

  def delete_old_artifacts(self):
    if 'migration_artifacts' in os.listdir('.'):
      shutil.rmtree('migration_artifacts')

  def download_manifests(self):
    print("\n\nDownloading manifests for selected certified operators... \n\n")
    cmd = ["offline-cataloger", "generate-manifests", "certified-operators"]
    process = subprocess.Popen(cmd)
    output = process.communicate()[0]
    process.wait()
    print("Done.")
    manifests_path = []
    [manifests_path.append(d) for d in os.listdir('.') if d.startswith('manifests-')]
    self.manifests_path = manifests_path

  def delete_unused_bundles(self):

    print("\n\n Selected bundles to migrate are: \n\n")

    for operator in self.operators:
      print("                " + operator)

    print("\n\n")

    print("\n\n...Deleting unused bundles...\n\n")
    bundles = []
    [bundles.append(bundle) for bundle in os.listdir(self.manifests_path[0])]
    for bundle in bundles:
      if bundle not in self.operators:
        shutil.rmtree(self.manifests_path[0] + "/" + bundle)
        print("Deleting " + bundle + "...")
    print("Done.")

  def nest_flat_operators(self):

    print("nesting selected flat paths\n\n")
    for operator in self.operators:
      if self.options[operator]["flat"]:
        os.rename(self.manifests_path[0] + "/" + operator, self.manifests_path[0] + "/" + operator + "-flat")
        cmd = ["operator-courier", "nest", self.manifests_path[0] + "/" + operator + "-flat", self.manifests_path[0] + "/" + operator]
        process = subprocess.Popen(cmd)
        output = process.communicate()[0]
        process.wait()
        print("nesting " + operator + " ......... Done.")

  def migrate_bundle_format(self):
    for operator in self.operators:
      selected_versions = self.options[operator]["versions"]
      bundle_path = self.manifests_path[0] + "/" + self.options[operator]["path"]
      for version in selected_versions:
        print("\n\nMigrating " + operator + ":" + version + "\n\n")
        cmd = ["opm", "alpha", "bundle", "generate", "--directory", bundle_path + "/" + version, "--output-dir", "migration_artifacts/" + operator + "/" + version]
        process = subprocess.Popen(cmd)
        output = process.communicate()[0]
        process.wait()
        os.system('echo "LABEL com.redhat.openshift.versions=\"v4.6,v4.5\"" >> bundle.Dockerfile')
        os.system('echo "LABEL com.redhat.delivery.operator.bundle=true" >> bundle.Dockerfile')
        if version == selected_versions[-1]:
          os.system('echo "LABEL com.redhat.delivery.backport=true" >> bundle.Dockerfile')
        shutil.move("bundle.Dockerfile", "migration_artifacts/" + operator + "/" + version + "/" + "bundle-" + version + ".Dockerfile")



def main():

  m = BundleMigration()
  m.update_manifests()
  m.delete_old_artifacts()
  m.migrate_bundle_format()

if __name__ == "__main__":
  main()