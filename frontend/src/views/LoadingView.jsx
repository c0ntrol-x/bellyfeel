import React from 'react'
import { Navbar, Nav, NavDropdown, NavItem, MenuItem, Col } from 'react-bootstrap';
var LoaderIMG = require("./loader.gif");


class LoadingView extends React.Component {
    render() {
        var self = this;
        var headerStyle = {
            color: '#5cbbff',
            paddingBottom: "2px",
        };
        return <center><h4 style={headerStyle}><img src={LoaderIMG} />{this.props.children}</h4></center>
    }
}

export default LoadingView
