# Operational Research Applications

This repository contains 2 applications developed using operational research techniques.

## Staff Scheduling Optimization

The Staff Scheduling Optimization application is designed to assist in scheduling employees based on various factors, such as availability, shift requirements, and costs. The tool provides an interface for inputting data like the number of employees, shifts, and days, as well as constraints such as maximum shifts per employee. The goal is to minimize the total cost of scheduling while meeting all operational requirements.

## Advertising Budget Allocation

The Advertising Budget Allocation application addresses the problem of optimally distributing a public advertising budget across multiple channels (Facebook, Instagram, TikTok, Online Ads) to maximize the number of conversions. The optimization takes into account budget constraints, minimum desired reach, and limits on the number of ads per channel.

Users can select the channels to include via a graphical interface, with at least two channels required. Results are displayed in terms of the budget allocated (in dollars) per channel, calculated as the product of the number of ads and the cost per ad—offering a more practical interpretation than simply showing the number of ads.

## How to Use

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python main.py
   ```
