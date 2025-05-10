# PidPal Desktop

  The current iteration of PidPal desktop will scrape and clean parcel data from each respective county website, clean the data from its original text format, and upload the data to the SQLite3 database. As it stands, each scrape of a parcel will overwrite the last, in its current version PidPal Desktop will not work as a year-over-year dashboard but as a one off security pricing tool.

![Project Screenshot](./Resources/readme_screenshot.png)

## Badges

[![Build Status](https://img.shields.io/github/actions/workflow/status/user/repo/test.yml?branch=main)](https://github.com/user/repo/actions)
[![Coverage Status](https://img.shields.io/coveralls/user/repo)](https://coveralls.io/github/user/repo)

## Table of Contents
- [Starting](#Starting)

## Starting
First navigate to the project directory then;
```bash
# Example
python -m pidpal.MAIN
