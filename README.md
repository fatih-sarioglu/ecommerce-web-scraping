# Codeway Case Study - Trendyol Web Scraping

## 1. Prepare the environment:
I sent you the project with the environment and required chromdriver.exe program in the zip file. I also uploaded the project on my GitHub if you want to check out. Below are instructions to run the project for both of the ways respectively:


#### From the zip file that I sent you:
As you can see, I ran the code and saved the data. If you want to run the code, please first take the output folder outside of this project folder or just delete it (there is a code line that creates that folder and if the folder already exists, it gives error). After, you can simply run the *main.py* and see the result for the full version.

#### From the GitHub repo:

If you get this project from GitHub you first need to set up the environment:
1. Create a python environment.
2. Activate the environment.
3. Install the dependencies in *requirements.txt* file. You may also install the python version I used (3.12.2).
4. Download the chromedriver.exe and locate it to this directory.

## 2. Run the code:

If you want to just test the code for a small run, you can do the following:
* Make the ``` testing = True``` and you can set ``` COMMENTS_UPPER_LIMIT ``` and ``` PRODUCTS_UPPER_LIMIT ``` to a small number.

* If you want to switch back to release mode (as it is asked in the case study), you just make the ``` testing = False ```.