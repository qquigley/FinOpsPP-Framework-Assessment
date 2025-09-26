# FinOps++ Framework Assessment

A FinOps Assessment perspective as a NIST CSF Community Profile

As organizations move their FinOps practices to shift-left, more of the FinOps optimization and maintenance tasks get pushed to the edge where the Engineers are. In this case, FinOps teams need to move their focus towards supporting the Inform and Operate phases of the FinOps lifecycle. Through building more formal FinOps Policies and Governance standards, FinOps teams can accelerate their iteration through the lifecycle phases to increase their practice maturity for the long run. Pulling inspiration from the Intersecting Discipline of Security, FinOps teams can solidify their position as a trusted partner to the business.

This assessment is an expansion of the existing FinOps Framework Assessment as of 7/3/25. By combining FinOps capabilities with controls found in the NIST Cybersecurity Framework, FinOps practitioners can provide a structured and proven foundation for strengthening governance for cost accountability. Additionally, treating financial risk with the same rigor as cybersecurity empowers FinOps teams to better define their policies, processes, and enforecement of best practices for the organization. 

# CLI Tool

To aid with formatting, transforming, and using the yaml specification, we built the `finopspp` CLI tool. This is a Python based tool that works for `Python >= 3.13`. Currently to use it, you have to build it from source from this repository. To do this, it is recommended that you start off by creating a virtual environment (venv) as is discussed in https://docs.python.org/3/library/venv.html. 

Once your venv is setup, [activate it](https://docs.python.org/3/library/venv.html#how-venvs-work) and run `python -m pip install -e .` from the same directory as this README. This command will pull in all required dependencies into your venv and then installs the script for you to use in your venv. It will also do this in what is called "[editable](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e)" mode. Which will allow you to change packages and files (including yaml specifications) used by `finopspp`, and to directly see those changes reflected in the invocation of the tool. Be careful when doing this, so as not to break the core functionality needed to generate the assessment.

## Developing the tool

If you use VSCode, or would like to, you can follow the tutorial from https://code.visualstudio.com/docs/python/python-tutorial to get started with setting up this python project environment. It is also recommended to read through https://realpython.com/python-pyproject-toml/ to get an overview of `pyproject.toml` based python projects. And to get a feel for the setup of this project in [pyproject.toml](/pyproject.toml) used for `finopspp`.


