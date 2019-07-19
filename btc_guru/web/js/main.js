function ajax_get(url, callback) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            try {
                var data = JSON.parse(xmlhttp.responseText);
            } catch (err) {
                console.log(err.message + " in " + xmlhttp.responseText);
                return;
            }
            callback(data);
        }
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function createChart(series) {
    Highcharts.stockChart('container', {
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
    createChart([{
        type: 'candlestick',
        name: 'BTC/USD',
        data: ohlc_data,
    }, {
        type: 'column',
        name: 'Volume',
        data: volume_data,
        yAxis: 1
    }])
});
