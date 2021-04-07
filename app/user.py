#!/usr/bin/env python3

from absl import logging
from urllib.parse import urlparse, urljoin
from google.protobuf.json_format import MessageToDict
from collections import namedtuple

from flask import Blueprint, render_template, flash, redirect, request
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from app.forms import UserForm, LoginForm, DeleteForm
from app.extensions import lm, mail, bcrypt
from app import util, channels

import grpc
from proto.steward import registry_pb2_grpc
from proto.steward import user_pb2 as u


bp = Blueprint("user", __name__)
logging.set_verbosity(logging.INFO)
users = channels.channel.user

@bp.route('/user/profile')
@login_required
def user_profile():
    return render_template('profile.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = UserForm()
    del form.old_password
    form.submit.label.text = 'Register'
    if form.validate_on_submit():
        user_submit(form)
        flash('User Created for {}'.format(form.email.data))
        return redirect('/login')
    if form.errors:
        logging.info('register failed for "{email}": {error}'.format(
            email = form.email.data,
            error = form.errors
            ))
        flash('register failed: {}'.format(form.errors))

    return render_template('user_edit.html', form=form, view='Register')

@bp.route('/user/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id=None):
    form = UserForm()
    form.submit.label.text = 'Update'

    if form.validate_on_submit():
        # check that old_password matches the current user's
        if bcrypt.check_password_hash(current_user.user.password, form.old_password.data):
            return user_submit(form, user_id)
        else:
            flash('Current password incorrect!')
    else:
        logging.info('loading current values because: {}'.format(form.errors))

        old_user = users.GetUser(u.GetUserRequest(_id=user_id))

        # All of this fuckery is needed because the proto object validates field types,
        # so we can't just change the field to a datetime object but need a new object
        user_dict = MessageToDict(message=old_user, preserving_proto_field_name=True)
        # Have to delete _id since it's not a valid field for a namedtuple
        del user_dict['_id']
        user_obj = namedtuple("User", user_dict.keys()) (*user_dict.values())
        form = UserForm(obj=user_obj)

    return render_template('user_edit.html', form=form, view='Edit User')



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        # This is the very first call a backend may be handling so worth being careful
        try:
            target_user = users.GetUser(u.GetUserRequest(email=form.email.data))
        except grpc._channel._InactiveRpcError as e:
            logging.warning('Instance had a stale channel: {channel}'.format(channel = channels.uri.user))
            global channel
            channels.refresh_all()
            channel = grpc.insecure_channel(channels.user)
            users = registry_pb2_grpc.UserServiceStub(channel)
            try:
                target_user = users.GetUser(u.GetUserRequest(email=form.email.data))
            except grpc._channel._InactiveRpcError as e:
                logging.error('Still had a stale channel, burning the house down')
                shutdown_server()
        if target_user.password and bcrypt.check_password_hash(target_user.password, form.password.data):
            user = WrappedUser()
            user.load(target_user)
            login_user(user)
            flash('Login succeeded for user {}'.format(form.email.data))

            next = util.get_redirect_target()
            return redirect(next)
        else:
            if target_user.email == form.email.data:
                sign = '=='
            else:
                sign = '!='
            logging.info('email login fail: "{target}" {sign} "{form}"'.format(
                target = target_user.email,
                form = form.email.data,
                sign = sign
                ))
            flash('Incorrect login details')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@lm.user_loader
def load_user(user_id):
    if user_id:
        user = WrappedUser(user_id)
        return user
    else:
        logging.error('load_user called without valid id!')

class WrappedUser(UserMixin):
    def __init__(self, user_id=None):
        # Need to modify stub if we've lost the connection
        global users
        if user_id:
            logging.debug('user created by id: {user_id}'.format(user_id=user_id))
            try:
                self.user = users.GetUser(u.User(_id=user_id))
            except grpc._channel._InactiveRpcError as e:
                logging.warning('Instance had a stale channel: {channel}'.format(channel = channels.uri.user))
                global channel
                channels.refresh_all()
                channel = grpc.insecure_channel(channels.user)
                users = registry_pb2_grpc.UserServiceStub(channel)
                try:
                    self.user = users.GetUser(u.User(_id=user_id))
                except grpc._channel._InactiveRpcError as e:
                    logging.error('Still had a stale channel, burning the house down')
                    shutdown_server()
        else:
            logging.debug('LazyLoading user')
            self.user = 'noneuser'
    def get_id(self):
        return self.user._id

    def load(self, proto):
        if proto:
            logging.debug('Loading user: {}'.format(proto))
            self.user = proto
        else:
            logging.error('Tried to load user with empty proto!')

def user_submit(form, user_id=None):
    if user_id:
        user = u.User()
    else:
        user = u.CreateUserRequest()
    user.name = form.name.data
    user.email = form.email.data
    user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

    if user_id:
        new_user = users.UpdateUser(u.UpdateUserRequest(_id=user_id, user=user))
    else:
        new_user = users.CreateUser(user)
    return redirect('/user/{}'.format(new_user._id))

