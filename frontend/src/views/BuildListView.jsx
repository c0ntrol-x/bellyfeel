import React from 'react'
import {connect} from 'react-redux';
import { Panel, Table } from 'react-bootstrap';
import APIClient from '../networking.jsx';


class BuildListView extends React.Component {
    propTypes: {
        builds: React.PropTypes.array,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.deleteBuild = this.deleteBuild.bind(this);
    }
    deleteBuild(build_id) {
        const {store} = this.context;
        this.api.deleteBuild(build_id, (build, err) => {
            store.dispatch({
                type: "BUILD_DELETED",
                build_id: build_id
            })
        }.bind(this));

    }
    render() {
        const builds = this.props.builds;
        return (
            <Panel header={"Builds"} bsStyle="primary">
                <Table striped condensed hover>
                    <thead>
                        <tr>
                            <th>status</th>
                            <th>started at</th>
                            <th>branch</th>
                            <th>actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_.map(builds, (build, i) => {
                            return (
                                <tr key={i}>
                                <td><code>{build.status}</code></td>
                                <td>{build.branch}</td>
                                <td>{build.started_at}</td>
                                <td><a href={"/#/build/" + build.id}>view/watch</a></td>
                                <td><a onClick={(e) => { e.preventDefault(); this.deleteBuild(build.id) }.bind(this)} href={build.id}>delete</a></td>
                                </tr>
                            )}
                         )}
                    </tbody>
                </Table>
            </Panel>
        );
    }
}
BuildListView.contextTypes = {
    store: React.PropTypes.object
};

export default BuildListView = connect(
    (state) => {
        return {
            builds: state.builds || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(BuildListView);
