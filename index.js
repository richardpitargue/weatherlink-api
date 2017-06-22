import cron from 'cron';
import logger from 'morgan';
import express from 'express';
import shell from 'python-shell'

import config from './config';
import db from './lib/database';

const CronJob = cron.CronJob;

const app = express();
app.use(logger('dev'));
app.set('port', process.env.PORT || config.PORT);

app.listen(app.get('port'), () => {
    console.log(config.APP_NAME + ' is listening on port ' + app.get('port'));
});

let options = {
    scriptPath: __dirname + '/'
}

// cron job to update weather data once every 15 minutes
let updateJob = new CronJob('0 */15 * * * *', () => {
    shell.run('main.py', options, (err, reslts) => {
        if(err) {
            console.log(err);
        } else {
            console.log('Weather data has been updated.')
        }
    });
}, null, true);

// GET returns all weather data on a specific date for the given stationId
app.get('/data/:stationId/on/:day-:month-:year', (req, res) => {
    let stationId = req.params.stationId;
    let date = {
        'day': parseInt(req.params.day),
        'month': parseInt(req.params.month),
        'year': parseInt(req.params.year)
    };

    if(!stationId) {
        return res.status(400).send({
            'message': 'Missing stationId from GET request (/data/:stationid)'
        });
    }

    db.connect(() => {
        db.get().collection('weather-data').find({
            'stationId': stationId,
            'date.day': date.day,
            'date.month': date.month,
            'date.year': date.year
        }).toArray((err, data) => {
            if(err) {
                return res.send(err);
            }

            if(data.length === 0) {
                return res.status(404).send({
                    'message': 'No data has been found for your query.'
                });
            }

            return res.send(data);
        });
    });
});

// GET returns all weather data for given stationId
app.get('/data/:stationId', (req, res) => {
    let stationId = req.params.stationId;

    if(!stationId) {
        return res.status(400).send({
            'message': 'Missing stationId from GET request (/data/:stationid)'
        });
    }

    db.connect(() => {
        db.get().collection('weather-data').find({
            'stationId': stationId
        }).toArray((err, data) => {
            if(err) {
                return res.send(err);
            }

            if(data.length === 0) {
                return res.status(404).send({
                    'message': 'No data has been found for your query.'
                });
            }

            return res.send(data);
        });
    });
});

// GET returns the rainfall summary on the given day
app.get('/data/:stationId/rainfall/:day-:month-:year', (req, res) => {
    let stationId = req.params.stationId;
    let date = {
        'day': parseInt(req.params.day),
        'month': parseInt(req.params.month),
        'year': parseInt(req.params.year)
    };

    if(!stationId) {
        return res.status(400).send({
            'message': 'Missing stationId from GET request (/data/:stationid)'
        });
    }

    db.connect(() => {
        db.get().collection('weather-data').find({
            'stationId': stationId,
            'date.day': date.day,
            'date.month': date.month,
            'date.year': date.year
        }).toArray((err, data) => {
            if(err) {
                return res.send(err);
            }

            if(data.length === 0) {
                return res.status(404).send({
                    'message': 'No data has been found for your query.'
                });
            }

            let min = data[0].data.rainfall;
            let max = 0;
            let ave = 0;

            for(let i = 0; i < data.length; i++) {
                ave += data[i].data.rainfall;
                if(data[i].data.rainfall < min) {
                    min = data[i].data.rainfall;
                } else if(data[i].data.rainfall > max) {
                    max = data[i].data.rainfall;
                }
            }
            ave /= data.length;

            return res.send({
                min,
                max,
                ave
            });
        });
    });
});

// GET returns the ET summary on the given day
app.get('/data/:stationId/evapotranspiration/:day-:month-:year', (req, res) => {
    let stationId = req.params.stationId;
    let date = {
        'day': parseInt(req.params.day),
        'month': parseInt(req.params.month),
        'year': parseInt(req.params.year)
    };

    if(!stationId) {
        return res.status(400).send({
            'message': 'Missing stationId from GET request (/data/:stationid)'
        });
    }

    db.connect(() => {
        db.get().collection('weather-data').find({
            'stationId': stationId,
            'date.day': date.day,
            'date.month': date.month,
            'date.year': date.year
        }).toArray((err, data) => {
            if(err) {
                return res.send(err);
            }

            if(data.length === 0) {
                return res.status(404).send({
                    'message': 'No data has been found for your query.'
                });
            }

            let min = data[0].data.ET;
            let max = 0;
            let ave = 0;

            for(let i = 0; i < data.length; i++) {
                ave += data[i].data.ET;
                if(data[i].data.rainfall < min) {
                    min = data[i].data.ET;
                } else if(data[i].data.ET > max) {
                    max = data[i].data.ET;
                }
            }
            ave /= data.length;

            return res.send({
                min,
                max,
                ave
            });
        });
    });
});

// GET returns the ET summary on the given day
app.get('/data/:stationId/waterdeficit/:day-:month-:year', (req, res) => {
    let stationId = req.params.stationId;
    let date = {
        'day': parseInt(req.params.day),
        'month': parseInt(req.params.month),
        'year': parseInt(req.params.year)
    };

    if(!stationId) {
        return res.status(400).send({
            'message': 'Missing stationId from GET request (/data/:stationid)'
        });
    }

    db.connect(() => {
        db.get().collection('weather-data').find({
            'stationId': stationId,
            'date.day': date.day,
            'date.month': date.month,
            'date.year': date.year
        }).toArray((err, data) => {
            if(err) {
                return res.send(err);
            }

            if(data.length === 0) {
                return res.status(404).send({
                    'message': 'No data has been found for your query.'
                });
            }

            let minET = data[0].data.ET;
            let maxET = 0;
            let aveET = 0;

            let minTemp = data[0].data.temp.min;
            let maxTemp = data[0].data.temp.max;
            let aveTemp = data[0].data.temp.ave;

            let minRainfall = data[0].data.rainfall;
            let maxRainfall = 0;
            let aveRainfall = 0;

            for(let i = 0; i < data.length; i++) {
                // ET
                aveET += data[i].data.ET;
                if(data[i].data.rainfall < minET) {
                    minET = data[i].data.ET;
                } else if(data[i].data.ET > maxET) {
                    maxET = data[i].data.ET;
                }

                // temperature
                minTemp += data[0].data.temp.min;
                maxTemp += data[0].data.temp.max;
                aveTemp += data[0].data.temp.ave;

                // rainfall
                aveRainfall += data[i].data.rainfall;
                if(data[i].data.rainfall < minRainfall) {
                    minRainfall = data[i].data.rainfall;
                } else if(data[i].data.rainfall > maxRainfall) {
                    maxRainfall = data[i].data.rainfall;
                }
            }
            aveET /= data.length;
            minTemp /= data.length;
            maxTemp /= data.length;
            aveTemp /= data.length;

            return res.send({
                'ET': {
                    'min': minET,
                    'max': maxET,
                    'ave': aveET
                },
                'temp': {
                    'min': minTemp,
                    'max': maxTemp,
                    'ave': aveTemp
                },
                'rainfall': {
                    'min': minRainfall,
                    'max': maxRainfall,
                    'ave': aveRainfall
                }
            });
        });
    });
});
