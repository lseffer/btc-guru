function ajax_get(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            try {
                var data = JSON.parse(xhr.responseText);
            } catch (err) {
                console.log(err.message + " in " + xhr.responseText);
                return;
            }
            callback(data);
        }
    };
    xhr.open("GET", url, true);
    xhr.send();
}

function create_ohlcv_chart(series, container_id) {
    Highcharts.stockChart(container_id, {
        rangeSelector: {
            buttons: [{
                type: 'hour',
                count: 12,
                text: '12h'
            }, {
                type: 'day',
                count: 1,
                text: '1d'
            }, {
                type: 'week',
                count: 1,
                text: '1w'
            }, {
                type: 'month',
                count: 1,
                text: '1m'
            }, {
                type: 'month',
                count: 3,
                text: '3m'
            }, {
                type: 'month',
                count: 6,
                text: '6m'
            }, {
                type: 'ytd',
                text: 'ytd'
            }, {
                type: 'year',
                count: 1,
                text: '1y'
            }, {
                type: 'all',
                text: 'all'
            }],
            selected: 3
        },
        yAxis: [{
            labels: {
                align: 'right',
                x: -3
            },
            title: {
                text: 'OHLC'
            },
            height: '60%',
            lineWidth: 2,
            resize: {
                enabled: true
            }
        }, {
            labels: {
                align: 'right',
                x: -3
            },
            title: {
                text: 'Volume'
            },
            top: '65%',
            height: '35%',
            offset: 0,
            lineWidth: 2
        }],
        title: {
            text: 'BTC/USD Historical'
        },
        tooltip: {
            split: true
        },
        series: series
    });
}

function create_prediction_chart(series, container_id) {
    Highcharts.stockChart(container_id, {
        rangeSelector: {
            buttons: [{
                type: 'hour',
                count: 12,
                text: '12h'
            }, {
                type: 'day',
                count: 1,
                text: '1d'
            }, {
                type: 'week',
                count: 1,
                text: '1w'
            }, {
                type: 'month',
                count: 1,
                text: '1m'
            }, {
                type: 'month',
                count: 3,
                text: '3m'
            }, {
                type: 'month',
                count: 6,
                text: '6m'
            }, {
                type: 'ytd',
                text: 'ytd'
            }, {
                type: 'year',
                count: 1,
                text: '1y'
            }, {
                type: 'all',
                text: 'all'
            }],
            selected: 3
        },
        title: {
            text: 'BTC/USD close vs. predicted close'
        },
        series: series
    });
}

ajax_get('./timeseries?fields=open,high,low,close,volume', function (data) {
    var cols = data["columns"]
    var time_index = cols.indexOf("time")
    var open_index = cols.indexOf("open")
    var high_index = cols.indexOf("high")
    var low_index = cols.indexOf("low")
    var close_index = cols.indexOf("close")
    var volume_index = cols.indexOf("volume")
    var ohlc_data = []
    var volume_data = []
    data["data"].forEach(function (row) {
        ohlc_data.push([row[time_index], row[open_index], row[high_index], row[low_index], row[close_index]])
        volume_data.push([row[time_index], row[volume_index]])
    });
    create_ohlcv_chart([{
        type: 'candlestick',
        name: 'BTC/USD',
        data: ohlc_data,
    }, {
        type: 'column',
        name: 'Volume',
        data: volume_data,
        yAxis: 1
    }],
        'ohlcv_container')
});

ajax_get('./timeseries?fields=predicted_close_absolute,close&result_limit=1000', function (data) {
    var cols = data["columns"]
    var time_index = cols.indexOf("time")
    var close_index = cols.indexOf("close")
    var predicted_close_index = cols.indexOf("predicted_close_absolute")
    var close_data = []
    var predicted_close_data = []
    data["data"].forEach(function (row) {
        if (row[close_index] !== null) {
            close_data.push([row[time_index], row[close_index]])
        }
        predicted_close_data.push([row[time_index], row[predicted_close_index]])
    });
    var txt = "The price of BTC/USD will go";
    var last_prediction = predicted_close_data.slice(-1)[0];
    var last_close = close_data.slice(-1)[0][1];
    var arrow_element = document.getElementById("arrow");
    if (last_prediction >= last_close) {
        var dt = new Date(last_prediction[0])
        txt = txt + " up to $" + last_prediction[1].toFixed(2) + " on " + dt.toUTCString()
        arrow_element.setAttribute("class", "arrow-up")
    } else {
        var dt = new Date(last_prediction[0])
        txt = txt + " down to $" + last_prediction[1].toFixed(2) + " on " + dt.toUTCString()
        arrow_element.setAttribute("class", "arrow-down")
    }
    var pred_text = document.getElementById("prediction_text")
    pred_text.innerText = txt
    create_prediction_chart([{
        name: 'BTC/USD Close',
        data: close_data,
        lineWidth: 2,
        tooltip: {
            valueDecimals: 2
        },
        states: {
            hover: {
                lineWidthPlus: 0
            }
        }
    }, {
        name: 'BTC/USD Predicted Close',
        data: predicted_close_data,
        lineWidth: 0,
        marker: {
            enabled: true,
            radius: 6,
            fillColor: '#8B0000'
        },
        tooltip: {
            valueDecimals: 2
        },
        states: {
            hover: {
                lineWidthPlus: 0
            }
        }
    }],
        'prediction_container')
});
