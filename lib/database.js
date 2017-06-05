import config from '../config';
import mongodb from 'mongodb';

const MongoClient = mongodb.MongoClient;

let state = {
    db: null
};

exports.connect = (done) => {
    if (state.db) return done();

    MongoClient.connect(config.DB_URL, function(err, db) {
        if (err) return done(err);
        state.db = db;
        done();
    });
}

exports.get = () => {
  return state.db;
};

exports.close = (done) => {
    if (state.db) {
        state.db.close((err, result) => {
            state.db = null;
            state.mode = null;
            done(err);
        });
    }
};
