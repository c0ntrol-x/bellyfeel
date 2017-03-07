import $ from 'jquery'
import _ from 'lodash'
import React from 'react'
import HeaderView from './HeaderView.jsx'
import LoadingView from './LoadingView.jsx'
import AuthenticatedView from './AuthenticatedView.jsx'
import ErrorView from './ErrorView.jsx'
import { Col, Panel } from 'react-bootstrap';
import {connect} from 'react-redux';
import {Button} from 'react-bootstrap';
import APIClient from '../networking.jsx';


class BuildDetailView extends React.Component {
    propTypes: {
        build: React.PropTypes.object,
    }
    constructor() {
        super();
        this.api = new APIClient();
        this.refresh = this.refresh.bind(this);
        this.retrieveBuild = this.retrieveBuild.bind(this);
    }
    refresh(){
        const {store} = this.context;
        this.retrieveBuild();
    }
    componentDidMount() {
        this.refresh();
        this.timer = window.setInterval(() => {
            this.refresh()
        }.bind(this), 5000);
    }
    componentWillUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }
    componentDidUpdate() {
            var node = $("#build-output")[0];
            node.scrollTop = node.scrollHeight;
    }
    retrieveBuild() {
        const {store} = this.context;
        this.api.getBuildById(this.props.params.build_id, (build, err) => {
            if (err) {
                store.dispatch({
                    ...builds,
                    type: "ERROR",
                });
            } else {
                store.dispatch({
                    build: build,
                    type: "BUILD_DETAILS",
                });
                if (build.builds.length > 0) {
                    store.dispatch({
                        builds: build.builds,
                        type: "LIST_BUILDS",
                    });
                }
            }
        });
    }
    render() {
        const {build} = this.props;
        return build.project ? (
        <AuthenticatedView>
            <HeaderView navigation={true} />
                <Col md={12}>
                <h3><a href={"/#/project/" + build.project.id}>{build.project.owner}/{build.project.name}</a> - build {build.id}</h3>
                </Col>
                <Col md={8}>
                    <Panel header={"output"} bsStyle="default">
                        <pre id="build-output" style={{maxHeight: "500px", overflowY: "auto"}}>{build.output}</pre>
                    </Panel>
                </Col>
                <Col md={4}>
                    <Panel header={"Status"} bsStyle={build.status !== "failed" ? "success": "warning"}>
                        <h4>status <code>{build.status}</code></h4>
                        <h4>exit code <code>{build.exit_code}</code></h4>
                    </Panel>
                    <Panel header={"Start/Finish"} bsStyle="default">
                        <h4>start <code>{build.started_at}</code></h4>
                        <h4>end <code>{build.finished_at}</code></h4>
                    </Panel>
                </Col>

        </AuthenticatedView>
        ) : <LoadingView>loading...</LoadingView>
    }
}

BuildDetailView.contextTypes = {
    store: React.PropTypes.object
};

export default BuildDetailView = connect(
    (state) => {
        return {
            build: state.currentBuild || {},
        }
    },
    (dispatch) => {
        return {
        }
    },
)(BuildDetailView);
