import React from 'react'
import { Navbar, Nav, NavDropdown, NavItem, MenuItem, Col } from 'react-bootstrap';
var Logo = require("./favicon-16.png");


class HeaderView extends React.Component {
    render() {
        var self = this;
        return (
            <Navbar>
                <Navbar.Header>
                    <Navbar.Brand>
                        <a href="/"><img src={Logo}/></a>
                    </Navbar.Brand>
                    <Navbar.Toggle />
                </Navbar.Header>
                {this.props.navigation ? <Navbar.Collapse>
                    <Nav>
                        <NavItem href="/">Browse Projects</NavItem>
                        <NavItem href="/logout">Logout</NavItem>
                    </Nav>

                </Navbar.Collapse> : null}
            </Navbar>
        )
    }
}

export default HeaderView
