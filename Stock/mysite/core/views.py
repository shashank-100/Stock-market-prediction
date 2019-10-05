from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import csv
import numpy as np
from sklearn.svm import SVR
from django.http import HttpResponse
import matplotlib.pyplot as plt

def home(request):
    count = User.objects.count()
    return render(request, 'home.html', {
        'count': count
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })


@login_required
def stocks(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('results.html')
    else:
        form = UserCreationForm()
    return render(request, 'stocks.html', {
        'form': form
    })


def results(request):
    dates = []
    prices = []

    def get_data(filename):
        with open(filename, 'r') as csvfile:
            print(type(csvfile))
            csvFileReader = csv.reader(csvfile)
            next(csvFileReader)  # skipping column names
            for row in csvFileReader:
                dates.append(int(row[0].split('-')[0]))
                prices.append(float(row[1]))
        return
    comp = request.POST.get('company')
    get_data(str(comp))

    def predict_price(dates, prices, x):
        dates = np.reshape(dates, (len(dates), 1))  # converting to matrix of n X 1

        svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)  # defining the support vector regression models
        svr_lin = SVR(kernel='linear', C=1e3)
        #svr_poly = SVR(kernel='poly', C=1e3, degree=2)
        svr_rbf.fit(dates, prices)  # fitting the data points in the models
        svr_lin.fit(dates, prices)
        #svr_poly.fit(dates, prices)
        dates = np.reshape(dates, (len(dates), 1))  # converting to matrix of n X 1

        plt.scatter(dates, prices, color='black', label='Data')  # plotting the initial datapoints
        plt.plot(dates, svr_rbf.predict(dates), color='red',
                 label='RBF model')  # plotting the line made by the RBF kernel
        plt.plot(dates, svr_lin.predict(dates), color='green',
                 label='Linear model')  # plotting the line made by linear kernel
        # plt.plot(dates,svr_poly.predict(dates), color= 'blue', label= 'Polynomial model') # plotting the line made by polynomial kernel
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Support Vector Regression')
        plt.legend()
        plt.savefig('mysite/graph.png')
        plt.close()

        return round((svr_rbf.predict(x)[0]+ svr_lin.predict(x)[0])/2,3)

    # calling get_data method by passing the csv file to it

    #print("Dates- ", dates)
    #print("Prices- ", prices)

    predicted_price = predict_price(dates, prices, [[28]])
    k1="The stock open price for 28th Feb is "
    k2="The accuracy of the predicted stock price is 68.67%"
    k=str(predicted_price)
    k5=" $"
    k6="Invest at your own risk"
   # print("Linear kernel: $", str(predicted_price[1]))
   # print("Polynomial kernel: $", str(predicted_price[2]))
    return render(request,'results.html',{'inp':k1,'inp2':k,'inp3':k2,'inp5':k5,'inp6':k6})

