# LSM microscope hardware controller 

This github will include the necessary software to control the different components of the LSM setup

## Environment

In order to use the software you will need to activate the environment created to control the dependencies version used. To activate the environment, open a console in the path were you clone the repository and run the command `.\lsm_env\Scripts\activate` 

If the environment is properly activated you will see the name of the environment before the path in the command line (example bellow)

![Activate venv](images_readme/activate_env.png)

If you got this error, 

![error activate venv](images_readme/error_venv.png)

Run the command `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force` and try to activate the environment again.

To deactivate the environment and return to the global Python environment, simply use the `deactivate` command.

## Napari

[Napari](https://napari.org) is a powerful library for n-dimensional image visualisation, annotation, and analysis. Hence, it is the selected tool for this project. To run it, just write the command `napari` in the console after activating the environment.