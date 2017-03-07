import React from 'react'
import APIClient from '../networking.jsx';
import { Panel, Button, Table } from 'react-bootstrap';


class ProjectListView extends React.Component {
    constructor() {
        super();
        this.api = new APIClient();
        this.triggerBuild = this.triggerBuild.bind(this);
        this.refresh = this.refresh.bind(this);
        this.retrieveProjects = this.retrieveProjects.bind(this);
    }
    triggerBuild(project_id) {
        this.api.triggerNewBuild(project_id, (project, err) => {
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
    refresh(){
        const {store} = this.context;
        store.dispatch({
            type: "CLEAR_ERRORS",
        });
        this.retrieveProjects();
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
    }
    render() {
        const projects = this.props.projects;
        return (
            <Panel header={"Managed Projects"} bsStyle="warning">
                <Table striped bordered condensed hover>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Owner</th>
                            <th>URI</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_.map(projects, (prj, i) => {
                            return (
                                <tr key={i} className={prj.status === "failed" ? "danger": ""}>
                                <td><a href={"/#/project/" + prj.id}>{prj.name}</a></td>
                                <td>{prj.owner}</td>
                                <td>{prj.git_url}</td>
                                <td>{prj.status}</td>
                                <td>
                                <a href={"/#/project/" + prj.id}>edit</a>
                                {prj.status.match(/published/) ? <span>&nbsp; | &nbsp; <a href={["docs", prj.owner, prj.name, "index.html"].join("/")}>view docs</a></span>: null}
                                {prj.status.match(/failed/) ? <span>&nbsp; | &nbsp; <a onClick={(e) => {this.triggerBuild(prj.id); e.preventDefault()}.bind(this)} href={location.href}>rebuild</a></span>: null}
                                </td>
                                </tr>
                            )}
                         )}
                    </tbody>
                </Table>
            </Panel>
        );
    }
}

export default ProjectListView
