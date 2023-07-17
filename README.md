![logo](docs/graphics/sa_logo.png)

*<p align="justify"><b>Semper Augustus</b> is a symbol of tulipomania - an economic phenomenon in 17th-century Holland. The extremely rare cabboules of this flower affected by tulip mottle virus disease met with a <b>huge increase in demand and prices</b> on the local market. It is believed to have been the first <b>speculative bubble</b>. Flowers then became a symbol of luxury and as well as social standing. In 1637, the speculative bubble burst, leading to many tragedies for people involved in speculation. <b>The collapse of the market was caused by excessive prices, for which there were no more takers</b>. The story is a valuable lesson for speculators and traders around the world...</p>*
<p align="center">. . .</p>
<p align="justify">This appilation was written to eliminate the human emotion factor from the trading process. It is a trading bot that allows algorithmic trading with the use of brokers' api. This solution can work with the models developed within this repository to take long and short positions depending on the market behavior. The use of multi-threading makes it possible to trade on multiple assets at the same time with minimal computational load. <b>It is planned to extend the functionality with arbitration.</b></p>

## Project status
<p align="justify">
The project currently provides a basis for developing real-time investment strategies. By default, the code has been adapted to use a demo account due to the risk of losses. The current state of the application makes it possible to use the framework to implement complex solutions. It includes:
<li>XTB broker api client</li> 
<li>Exchange data streaming module </li>
<li>Purchase decision model - moving averages</li> 
<li>Position closing model</li> 
<li>Module for conducting multiple trading sessions simultaneously using multithreading </li> <br>
The next steps will be to:
<li>Development of portfolio risk management modules</li> 
<li>Machine learning-based method of catching inefficiencies in a trading platform to avoid losses caused by its malfunctioning</li>
<li>Development of other investment methods</li>

## Tests status
<p align="justify">
Status of unit tests for Python 3.9 and 3.19 on the most recent versions of Ubuntu and Windows:</p>
<img src="https://github.com/dominikteodorczyk/SemperAugustus/actions/workflows/tests.yml/badge.svg" alt="Badge">
Tests include unit tests and syntax checking with flake8 and static typing with mypy.
</p>

## Installation Instructions
<p align="justify">
1. Make sure you have Python version 3.9 or 3.10 installed (confirmed to work by testing). You can check this by running the following command on the command line:<br>
<code>python --version</code><br>
If Python is not installed or you have an older version, visit the official Python website (https://www.python.org) and follow the installation instructions for your operating system.<br>
2. Clone the project repository from GitHub using the command:<br>
<code>git clone https://github.com/dominikteodorczyk/SemperAugustus.git</code><br>
You can also download the repository as a ZIP file and unzip it on your computer.<br>
3. We recommend creating a virtual Python environment to isolate the project's dependencies. You can do this by running the following command:<br>
<code>python -m venv venv</code><br>
This command will create a virtual environment named "venv" in the project directory.<br>
4. install the required project dependencies using pip package manager:<br>
<code>pip install -r requirements.txt</code><br>
This command will download and install all the required modules and libraries that the project requires for proper operation. The `requirements.txt` file should be located in the project's root directory and contain a list of dependencies with their versions.<br>
<b>5. Modify the '.exampleevn' file according to the instructions therein and rename it to '.evn'.</b><br>
6. The project has been successfully installed!




</p>

![image](docs/graphics/in_progress.png)

