import React from "react";
import { NavLink } from "react-router-dom";
import logo from '../pulsar_logo.svg';


function Navigation() {
    return (
        <div id='navigation'>
            <nav>
                <img id='nav-logo' alt='company logo' src={logo}/>
                <NavLink className='navLink' to="/">Control</NavLink>
                <NavLink className='navLink' to="/setup">Setup</NavLink>
            </nav>
            <hr/>
        </div>
    );
}

export default Navigation;