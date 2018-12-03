from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from feeds.auth import login_required
from feeds.db import get_db

from datetime import datetime
import time

bp = Blueprint('main', __name__)


@bp.route('/', methods=['POST', 'GET'])
@login_required
def index():

    d = datetime.strftime(datetime.now(), '%Y-%m-%d')
    t = datetime.strftime(datetime.now(), '%H:%M')

    now = {'day': d, 'time': t}

    db = get_db()

    if request.method == 'POST':
        feed_date = request.form['feed_date']
        feed_time = request.form['feed_time']
        action = request.form['action']
        feed_vol = request.form['feed_vol']

        feed_timestamp = feed_date + ' ' + feed_time
        feed_timestamp = datetime.strptime(feed_timestamp, '%Y-%m-%d %H:%M')
        feed_timestamp = time.mktime(feed_timestamp.timetuple())

        db.execute(
            'INSERT INTO action ('
            '  action_desc,'
            '  action_timestamp,'
            '  action_feedvol'
            ' )'
            ' VALUES (?, ?, ?)',
            (action, feed_timestamp, feed_vol,)
        )

        db.commit()
        return redirect(url_for('main.index'))

    return render_template('feeds/index.html', now=now)


@bp.route('/last-5-feeds')
@login_required
def last_5():

    title = {'title': 'Last 5 Feeds'}

    db = get_db()

    actions = db.execute(
        'SELECT * FROM action WHERE action_desc = "feed"'
        ' ORDER BY action_timestamp desc'
    ).fetchall()

    return render_template('feeds/actions.html', actions=actions, title=title)


@bp.route('/all-events/<status>')
@login_required
def all_actions(status):

    title = {'title': 'All Events'}

    db = get_db()

    actions = db.execute(
        'SELECT * FROM action ORDER BY action_timestamp DESC'
    ).fetchall()

    return render_template(
        'feeds/actions.html',
        actions=actions,
        title=title,
        status=status
    )


@bp.route('/last-feed')
@login_required
def last_feed():

    title = {'title': 'Last Feed'}

    db = get_db()

    actions = db.execute(
        'SELECT * from action WHERE action_desc = "feed"'
        ' ORDER by action_timestamp desc'
    ).fetchone()

    # t = time.time()
    f = actions['action_timestamp']
    t = 1542060605
    #   f = 1000000000
    delta = t - f

    return render_template(
        'feeds/last_feed.html',
        actions=actions,
        title=title,
        delta=delta,
    )


@bp.route('/delete/<id>')
@login_required
def delete(id):
    db = get_db()
    db.execute(
        'DELETE FROM action WHERE action_id=?',
        (id,)
    )

    db.commit()

    return redirect(url_for('main.all_actions', status='edit'))
