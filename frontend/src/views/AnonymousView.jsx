import React from 'react'
import HeaderView from './HeaderView.jsx'
import { Panel, Col } from 'react-bootstrap';

class AnonymousView extends React.Component {
    render() {
        return <div className="container">
    <HeaderView authenticated={false} />
    <Col md={3}></Col>
    <Col md={6}>
            <Panel header={"Not Authorized"} bsStyle="danger">
                <p>You must <a href="/login">login</a> in order to access the docs.</p>
                <p>Access is denied for users who don't belong to the <code>cnry</code> github organization.</p>
                <hr />
                <p><a className="btn btn-large btn-danger" href="/login">Github Login</a></p>

            </Panel>
        </Col>
    <Col md={3}></Col>
        </div>
    }
}

export default AnonymousView
