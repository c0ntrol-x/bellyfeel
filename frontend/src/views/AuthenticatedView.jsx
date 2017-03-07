import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import AnonymousView from './AnonymousView.jsx'
import { Col, Panel } from 'react-bootstrap';
import {connect} from 'react-redux';


class AuthenticatedView extends React.Component {
    propTypes: {
        user_token: React.PropTypes.string,
    }
    render() {
        const {user_token} = this.props;
        return (user_token.length > 8 ? <div className="container">{this.props.children}</div> : <AnonymousView />)
    }
}

AuthenticatedView.contextTypes = {
    store: React.PropTypes.object
};

export default AuthenticatedView = connect(
    (state) => {
        return {
            user_token: state.user_token || [],
        }
    },
    (dispatch) => {
        return {
        }
    },
)(AuthenticatedView);
