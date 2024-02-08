import autothesis.parser as parser
import mistlib as mist
import os
from myna.workflow.load_input import load_input
import argparse
import sys
import shutil


def configure_case(case_dir, res, myna_input="myna_data.yaml"):
    # Load input file
    input_path = os.path.join(case_dir, myna_input)
    settings = load_input(input_path)

    # Get part and layer info
    part = list(settings["build"]["parts"].keys())[0]
    layer = list(settings["build"]["parts"][part]["layer_data"].keys())[0]

    # Copy template case
    template_path = os.path.join(
        os.environ["MYNA_INTERFACE_PATH"], "thermal_part", "3dthesis", "template"
    )
    files = os.listdir(template_path)
    for f in files:
        source = os.path.join(template_path, f)
        dest = os.path.join(case_dir, f)
        shutil.copy(source, dest, follow_symlinks=True)

    # Set up scan path
    myna_scanfile = settings["build"]["parts"][part]["layer_data"][layer]["scanpath"][
        "file_local"
    ]
    case_scanfile = os.path.join(case_dir, "Path.txt")
    shutil.copy(myna_scanfile, case_scanfile)

    # Set up material properties
    material = settings["build"]["build_data"]["material"]["value"]
    material_dir = os.path.join(
        os.environ["MYNA_INSTALL_PATH"], "resources", "mist_material_data"
    )
    try:
        mistPath = os.path.join(material_dir, f"{material}.json")
        mistMat = mist.core.MaterialInformation(mistPath)
        mistMat.write_3dthesis_input(os.path.join(case_dir, "Material.txt"))
    except:
        raise Exception(f'Material "{material}" not found in mist material database.')

    # Set preheat temperature
    preheat = settings["build"]["build_data"]["preheat"]["value"]
    parser.adjust_parameter(os.path.join(case_dir, "Material.txt"), "T_0", preheat)

    # Set beam data
    beam_file = os.path.join(case_dir, "Beam.txt")
    spot_size = settings["build"]["parts"][part]["spot_size"]["value"]
    spot_unit = settings["build"]["parts"][part]["spot_size"]["unit"]
    spot_scale = 1
    if spot_unit == "mm":
        spot_scale = 1e-3
    elif spot_unit == "um":
        spot_scale = 1e-6
    power = settings["build"]["parts"][part]["laser_power"]["value"]
    parser.adjust_parameter(beam_file, "Width_X", spot_size * spot_scale)
    parser.adjust_parameter(beam_file, "Width_Y", spot_size * spot_scale)
    parser.adjust_parameter(beam_file, "Power", power)

    # Update domain resolution
    domain_file = os.path.join(case_dir, "Domain.txt")
    parser.adjust_parameter(domain_file, "Res", res)

    return


def main(argv=None):
    # Set up argparse
    parser = argparse.ArgumentParser(
        description="Launch autothesis for " + "specified input file"
    )
    parser.add_argument(
        "--res",
        default=12.5e-6,
        type=float,
        help="(float) resolution to use for simulations in meters",
    )

    # Parse command line arguments
    args = parser.parse_args(argv)
    settings = load_input(os.environ["MYNA_RUN_INPUT"])
    res = args.res

    # Get expected Myna output files
    step_name = os.environ["MYNA_STEP_NAME"]
    myna_files = settings["data"]["output_paths"][step_name]

    # Run autothesis for each case
    for case_dir in [os.path.dirname(x) for x in myna_files]:
        configure_case(case_dir, res)


if __name__ == "__main__":
    main(sys.argv[1:])
