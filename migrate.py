#! /usr/bin/env python3

import yaml
import subprocess
import os
import shutil

def load_config():
  with open("config.yaml") as config:
    parsed_yaml = yaml.load(config, Loader=yaml.FullLoader)
  return parsed_yaml

def delete_old_manifests():
  manifests_path = []
  [shutil.rmtree(d) for d in os.listdir('.') if d.startswith('manifests-')]

def download_manifests():
  print("\n\nDownloading manifests for selected certified operators... \n\n")
  cmd = ["offline-cataloger", "generate-manifests", "certified-operators"]
  process = subprocess.Popen(cmd)
  output = process.communicate()[0]
  process.wait()
  print("Done.")
  manifests_path = []
  [manifests_path.append(d) for d in os.listdir('.') if d.startswith('manifests-')]
  return manifests_path[0]

def select_bundles(manifests_path, config):

  selected_operators = config["selected_operators"]
  print("\n\n Selected bundles to migrate are: \n\n")

  for operator in selected_operators:
    print("                " + operator)

  print("\n\n")

  bundles = []
  [bundles.append(bundle) for bundle in os.listdir(manifests_path)]
  for bundle in bundles:
    if bundle not in selected_operators:
      shutil.rmtree(manifests_path + "/" + bundle)

def nest_flat_operators(manifests_path, config):

  print("nesting selected flat paths\n\n")

  flat_paths = config["flat_operators"]
  for operator in flat_paths:
    os.rename(manifests_path + "/" + operator, manifests_path + "/" + operator + "-flat")
    cmd = ["operator-courier", "nest", manifests_path + "/" + operator + "-flat", manifests_path + "/" + operator]
    process = subprocess.Popen(cmd)
    output = process.communicate()[0]
    process.wait()
    print("nesting " + operator + " ......... Done.")

def migrate_bundle_format(manifests_path, config):
  selected_operators = config["selected_operators"]
  for operator in selected_operators:
    selected_versions = config[operator]["versions"]
    bundle_path = manifests_path + "/" + config[operator]["path"]
    for version in selected_versions:
      print("\n\nMigrating " + operator + ":" + version + "\n\n")
      cmd = ["opm", "alpha", "bundle", "generate", "--directory", bundle_path + "/" + version, "migrated_artifacts/" + operator + "/" + version]
      process = subprocess.Popen(cmd)
      output = process.communicate()[0]
      process.wait()
      os.system('echo "LABEL com.redhat.openshift.versions=\"v4.6,v4.5\"" >> bundle.Dockerfile')
      os.system('echo "LABEL com.redhat.delivery.operator.bundle=true" >> bundle.Dockerfile')
      if version == selected_versions[-1]:
        os.system('echo "LABEL com.redhat.delivery.backport=true" >> bundle.Dockerfile')
      shutil.move("bundle.Dockerfile", "migrated_artifacts/" + operator + "/" + version + "bundle-" + version + ".Dockerfile")



def main():

  delete_old_manifests()

  config = load_config()
  manifests_path = download_manifests()

  select_bundles(manifests_path, config)
  nest_flat_operators(manifests_path, config)
  migrate_bundle_format(manifests_path, config)

if __name__ == "__main__":
  main()