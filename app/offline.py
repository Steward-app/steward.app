from absl import logging
from flask import Blueprint, render_template, flash, redirect, request
from flask_login import login_required, current_user

import grpc
from proto.steward import registry_pb2_grpc
from proto.steward import maintenance_pb2 as m
from proto.steward import asset_pb2 as a
from proto.steward import schedule_pb2 as s

from app import channels

bp = Blueprint("offline", __name__)

logging.set_verbosity(logging.INFO)

maintenances = channels.channel.maintenance
assets = channels.channel.asset
schedules = channels.channel.schedule

@bp.route('/offline')
def offline():
    return render_template('offline.html', maintenances=maintenances.ListMaintenances(m.ListMaintenancesRequest()))

