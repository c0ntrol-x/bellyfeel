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


class ProjectCreateView extends React.Component {
    propTypes: {
        project: React.PropTypes.object,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.doCreate = this.doCreate.bind(this);
    }
    doCreate() {
        this.api.createProject(data, (project, err) => {
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
    }
    render() {
        const {project} = this.props;
        return (
            <AuthenticatedView>
                <HeaderView navigation={true} />
                <Col md={12}>
                <Panel header={"add new project"} bsStyle="default">
                    <p>make sure to fill all the required fields</p>
                        <form className="form-horizontal" onSubmit={this.doCreate}>
                            <div className="form-group">
                                <label for="git-url" className="col-sm-2 control-label">github ssh url:</label>
                                <div className="col-sm-10">
                                    <input id="git-url" type="git_url" className="form-control" placeholder="git@github.com:..." />
                                </div>
                            </div>
                            <div className="form-group">
                                <label for="private-key" className="col-sm-2 control-label">private ssh key:</label>
                                <div className="col-sm-10">
                                    <textarea id="private-key" type="private_key" className="form-control"></textarea>
                                </div>
                            </div>
                            <div className="form-group">
                                <label for="public-key" className="col-sm-2 control-label">public ssh key:</label>
                                <div className="col-sm-10">
                                    <textarea id="public-key" type="public_key" className="form-control"></textarea>
                                </div>
                            </div>
                            <div className="form-group">
                                <label for="save_new_project" className="col-sm-2 control-label"></label>
                                <div className="col-sm-10">
                                    <Button id="save_new_project" bsStyle="default" onClick={this.doCreate}>Create</Button>
                                </div>
                            </div>
                        </form>
                    </Panel>
                </Col>
            </AuthenticatedView>
        )
    }
}

ProjectCreateView.contextTypes = {
    store: React.PropTypes.object
};

export default ProjectCreateView = connect(
    (state) => {
        return {
            project: state.currentProject || {},
        }
    },
    (dispatch) => {
        return {
        }
    },
)(ProjectCreateView);
