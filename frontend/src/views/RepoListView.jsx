import React from 'react'
import {connect} from 'react-redux';
import { Panel, Table } from 'react-bootstrap';


class RepoListView extends React.Component {
    propTypes: {
        repos: React.PropTypes.array,
    }
    render() {
        const repos = this.props.repos;
        return (
            <Panel header={"Github Repositories"} bsStyle="default">
                <div style={{"maxHeight": "220px", "overflowY": "auto"}}>
                <Table striped condensed hover>
                    <tbody>
                        {_.map(repos, (prj, i) => {
                            return (
                                <tr key={i}>
                                <td>{prj.name}</td>
                                </tr>
                            )}
                         )}
                    </tbody>
                </Table>
                </div>
            </Panel>
        );
    }
}
RepoListView.contextTypes = {
    store: React.PropTypes.object
};

export default RepoListView = connect(
    (state) => {
        return {
            repos: state.repos || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(RepoListView);
