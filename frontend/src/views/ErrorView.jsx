import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import {Panel} from 'react-bootstrap';
import {connect} from 'react-redux';
import APIClient from '../networking.jsx';


class ErrorView extends React.Component {
    propTypes: {
        errors: React.PropTypes.array,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.refresh = this.refresh.bind(this);
    }
    refresh(){
    }
    componentDidMount() {
        this.refresh();
    }
    render() {
        const {errors} = this.props;
        return (
            <Panel header={"Errors (" + errors.length + ")"} bsStyle={"danger"}>
                <div style={{"maxHeight": "300px", "overflowY": "auto"}}>
                {_.map(errors, (err, i) => {
                    return <pre key={i}>{err.message}</pre>
                 })}
                </div>
            </Panel>
        )
    }
}

ErrorView.contextTypes = {
    store: React.PropTypes.object
};

export default ErrorView = connect(
    (state) => {
        return {
            errors: state.errors || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(ErrorView);
