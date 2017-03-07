import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import HeaderView from './HeaderView.jsx'
import LoadingView from './LoadingView.jsx'
import AuthenticatedView from './AuthenticatedView.jsx'
import ProjectListView from './ProjectListView.jsx'
import BuildListView from './BuildListView.jsx'
import ErrorView from './ErrorView.jsx'
import { Col, Panel } from 'react-bootstrap';
import {connect} from 'react-redux';
import {Button} from 'react-bootstrap';
import APIClient from '../networking.jsx';


class ProjectDetailView extends React.Component {
    propTypes: {
        project: React.PropTypes.object,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.refresh = this.refresh.bind(this);
        this.retrieveProject = this.retrieveProject.bind(this);
        this.editProject = this.editProject.bind(this);
        this.deleteProject = this.deleteProject.bind(this);
        this.regenerateKeys = this.regenerateKeys.bind(this);
        this.triggerNow = this.triggerNow.bind(this);
    }
    refresh(){
        const {store} = this.context;
        this.retrieveProject();
    }
    triggerNow(e) {
        e.preventDefault();

        const {store} = this.context;
        this.api.triggerNewBuild(this.props.params.project_id, (project, err) => {
            if (err) {
                store.dispatch({
                    ...project,
                    type: "ERROR",
                });
            } else {
                store.dispatch({
                    project: project,
                    type: "PROJECT_DETAILS",
                });
            }
        });
    }
    editProject(e) {
        const {store} = this.context;

        e.preventDefault();
        const data = {
            documentation_path: $("#documentation-path").val(),
            requirements_path: $("#requirements-path").val(),
        }
        this.api.editProject(this.props.params.project_id, data, (project, err) => {
            if (err) {
                store.dispatch({
                    ...project,
                    type: "ERROR",
                });
            } else {
                store.dispatch({
                    project: project,
                    type: "PROJECT_DETAILS",
                });
            }
        });
    }
    regenerateKeys() {
        const {store} = this.context;
        this.api.regenerateKeysForProject(this.props.params.project_id, (project, err) => {
            if (err) {
                store.dispatch({
                    ...project,
                    type: "ERROR",
                });
            } else {
                store.dispatch({
                    project: project,
                    type: "PROJECT_DETAILS",
                });
            }
        });

    }
    componentDidMount() {
        this.refresh();
        this.timer = window.setInterval(() => {
            this.refresh()
        }.bind(this), 15000);
    }
    componentWillUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }
    deleteProject() {
        this.api.deleteProject(this.props.params.project_id, (project, err) => {
            this.props.history.push("/");
        }.bind(this));
    }
    retrieveProject() {
        const {store} = this.context;
        this.api.getProjectById(this.props.params.project_id, (project, err) => {
            if (err) {
                store.dispatch({
                    ...projects,
                    type: "ERROR",
                });
            } else {
                store.dispatch({
                    project: project,
                    type: "PROJECT_DETAILS",
                });
                if (project.builds.length > 0) {
                    store.dispatch({
                        builds: project.builds,
                        type: "LIST_BUILDS",
                    });
                }
            }
        });
    }
    render() {
        const {project} = this.props;
        return (
            <AuthenticatedView>
                <HeaderView navigation={true} />
                <Col md={12}>
                <h3><a href={["https://github.com", project.owner, project.name].join("/")}>{project.owner}/{project.name}</a></h3>

                </Col>
                <Col md={12}>
                <Panel header={"Details"} bsStyle="warning">
                    <Col md={6}>
                        <h4>Name</h4>
                        <pre>{project.name}</pre>
                        <h4>Owner</h4>
                        <pre>{project.owner}</pre>
                    </Col>
                    <Col md={6}>
                        <h4>Last Status</h4>
                        <pre>{project.status}</pre>
                    </Col>
                    <Col md={12}>
                        <h4>Hook URL</h4>
                        <p><strong>Copy the url below and set as web hook in your github project <a href={["https://github.com", project.owner, project.name, "settings/hooks"].join("/")}>settings</a>:</strong></p>
                        <pre><strong><a href={project.hook_url}>{project.hook_url}</a></strong></pre>
                    </Col>
                </Panel>
                </Col>
                <Col md={6}>
                    <Panel header={"Manage"} bsStyle="info">
                        <form className="form-horizontal" onSubmit={this.editProject}>
                        <h4>Documentation Path</h4>
                            <input id="documentation-path" type="text" className="form-control" placeholder={project.documentation_path || "./docs/"} />

                        <h4>Requirements Path</h4>
                            <input id="requirements-path" type="text" className="form-control" placeholder={project.requirements_path || "development.txt"}/>

                        <h4>Hook URL</h4>

                        {project.status === "published" ? <span><a className="btn btn-primary" href={["docs", project.owner, project.name, "index.html"].join("/")}>view documentation</a>&nbsp;&nbsp;&nbsp;</span>: null}
                        <Button onClick={this.triggerNow} bsStyle={"info"}>Request Build</Button>


                        &nbsp;
                        &nbsp;
                        &nbsp;
                        <Button onClick={this.editProject} bsStyle={"warning"}>Edit</Button>
                        &nbsp;
                        &nbsp;
                        &nbsp;
                        <Button onClick={this.deleteProject} bsStyle={"danger"}>Delete Project</Button>
                        </form>
                    </Panel>

                </Col>

                <Col md={6}>
                    <BuildListView />
                </Col>
            </AuthenticatedView>
        )
    }
}

ProjectDetailView.contextTypes = {
    store: React.PropTypes.object
};

export default ProjectDetailView = connect(
    (state) => {
        return {
            project: state.currentProject || {},
        }
    },
    (dispatch) => {
        return {
        }
    },
)(ProjectDetailView);
