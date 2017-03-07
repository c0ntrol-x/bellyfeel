import $ from 'jquery'
import React from 'react'
import {connect} from 'react-redux';
import { Panel, Table, FormControl, FormGroup, Button, ControlLabel, Col, Checkbox } from 'react-bootstrap';
import HeaderView from './HeaderView.jsx'
import {Typeahead} from 'react-typeahead';
import APIClient from '../networking.jsx';

const NAMEREGEX = new RegExp('^[a-zA-Z0-9_-]+[/][a-zA-Z0-9_-]+$');


class AddProjectView extends React.Component {
    propTypes: {
        repos: React.PropTypes.array,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.doImportProject = this.doImportProject.bind(this)
    }
    doImportProject(e){
        e.preventDefault();
        const {store} = this.context;

        const name = $("#project-name").val();
        const documentation_path = $("#documentation-path").val();
        const requirements_path = $("#requirements-path").val();

        if (!name.match(NAMEREGEX)) {
            store.dispatch({
                message: "import project: repository name match format 'owner/user', got: " + name,
                type: "ERROR",
            });
            return;
        }
        this.api.importProject(name, (data, err) => {
            if (!err) {
                $("#project-name").val("");
            } else {
                store.dispatch({
                    ...data,
                    type: "ERROR",
                });
            }

        });

    }
    render() {
        return <Panel header={"Import a project from github"} bsStyle="default">
            <Col md={12}>
                <form className="form-horizontal" onSubmit={this.doImportProject}>
                    <div className="form-group">
                        <label className="control-label">The latest <strong>master</strong> archive will be downloaded via Github API</label>
                        <input id="project-name" type="name" className="form-control" placeholder="owner/name" />
                    </div>
                    <div className="form-group">
                        <label className="control-label"><strong>DOCUMENTATION PATH</strong></label>
                        <p><em>Optional. If not provided, this system will look for a path containing a <code>conf.py</code> file.</em></p>
                        <input id="documentation-path" type="documentation_path" className="form-control" placeholder="docs/" />
                    </div>
                    <div className="form-group">
                        <label className="control-label"><strong>REQUIREMENTS PATH</strong></label>
                        <p><em>Optional. If not provided, this system search for a <code>development.txt</code> or a <code>requirements.txt</code>, in that order.</em></p>
                        <input id="requirements-path" type="requirements_path" className="form-control" placeholder="requirements.txt" />
                    </div>
                    <div className="form-group">
                        <Button id="save_new_project" bsStyle="warning" onClick={this.doImportProject}>Import from github</Button>
                    </div>
                </form>
            </Col>
        </Panel>
    }
}

AddProjectView.contextTypes = {
    store: React.PropTypes.object
};

export default AddProjectView = connect(
    (state) => {
        return {
            repos: state.repos || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(AddProjectView);
