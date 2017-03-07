import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import HeaderView from './HeaderView.jsx'
import LoadingView from './LoadingView.jsx'

import AuthenticatedView from './AuthenticatedView.jsx'
import ProjectListView from './ProjectListView.jsx'
import AddProjectView from './AddProjectView.jsx'
import RepoListView from './RepoListView.jsx'

import ErrorView from './ErrorView.jsx'

import { Col, Panel, Button } from 'react-bootstrap';
import {connect} from 'react-redux';

import APIClient from '../networking.jsx';


class DashboardView extends React.Component {
    propTypes: {
        projects: React.PropTypes.array,
        repos: React.PropTypes.array,
        errors: React.PropTypes.array,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.refresh = this.refresh.bind(this);
        this.retrieveProjects = this.retrieveProjects.bind(this);
    }
    refresh(){
        const {store} = this.context;
        store.dispatch({
            type: "CLEAR_ERRORS",
        });
        this.retrieveProjects();
    }
    componentDidMount() {
        this.timer = setInterval(() => {
            this.refresh();
        }.bind(this), 10000);
        this.refresh();
    }
    retrieveProjects() {
        const {store} = this.context;
        this.api.retrieveProjects((result, err) => {
            if (err) {
                store.dispatch({
                    ...result,
                    type: "ERROR",
                });
            } else {
                store.dispatch({
                    projects: result,
                    type: "LIST_PROJECTS",
                });
            }
        });
        this.api.retrieveOrganizationRepos('cnry', (result, err) => {
            if (err) {
                store.dispatch({
                    ...result,
                    type: "ERROR",
                });
            } else {
                store.dispatch({
                    repos: result,
                    type: "LIST_REPOS",
                });
            }
        });
    }
    render() {
        const {projects, repos, errors} = this.props;
        return (
            <AuthenticatedView>
                <HeaderView navigation={true} />
                <Col md={12}>
                    <ProjectListView projects={projects} />
                </Col>
                <Col md={6}>
                    <AddProjectView repos={repos} />
                </Col>
                <Col md={6}>
                    {errors.length > 0 ? <ErrorView /> : null}
                </Col>
            </AuthenticatedView>
        )
    }
}

DashboardView.contextTypes = {
    store: React.PropTypes.object
};

export default DashboardView = connect(
    (state) => {
        return {
            projects: state.projects || [],
            repos: state.repos || [],
            errors: state.errors || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(DashboardView);
