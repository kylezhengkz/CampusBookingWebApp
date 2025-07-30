import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Button from '@mui/material/Button';
import { useRef, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { useAuth } from "../../../wrappers/AuthContext";
import { AccountMenu } from '../accountMenu/AccountMenu';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import "./Header.css";

export function Header() {
    const navigate = useNavigate();
    const location = useLocation();
    const { authUserId, setAuthUserId, username, setUsername, userPerm, setUserPerm, logout } = useAuth();

    const [showProfile, setShowProfile] = useState(false);
    const [showNavBar, setShowNavBar] = useState(false);
    const isLogin = authUserId !== null;

    const profileIconRef = useRef(null);

    // back button destinations
    const backRoutes = {
        "/viewBooking": "/home",
        "/cancelBooking": "/home",
        "/bookingHistory": "/home",
        "/login": "/",
        "/signup": "/",
        "/editAccount": "/home",
        "/adminPage": "/home",
        "/manageRooms": "/adminPage",
        "/manageBuildings": "/adminPage",
        "/viewAdminLog": "/adminPage"
    };

    const backTarget = backRoutes[location.pathname];
    const showBackButton = !!backTarget;

    const [anchorEl, setAnchorEl] = useState(null);
    const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
    const handleMenuClose = () => setAnchorEl(null);

    console.log("Current pathname:", location.pathname);

    return (
        <Box sx={{ flexGrow: 1 }}>
            <AppBar position="static">
                <Toolbar>
                    {/* Back Button */}
                    {showBackButton && (
                        <Button
                            color="inherit"
                            sx={{ mr: 2, fontWeight: "bold" }}
                            onClick={() => navigate(backTarget)}
                        >
                            ← Back
                        </Button>
                    )}

                    <IconButton
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="menu"
                        sx={{ mr: 2 }}
                        onClick={handleMenuOpen}
                    >
                        <MenuIcon />
                    </IconButton>

                    <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: "bold" }}>
                        Room Booking App
                    </Typography>

                    {authUserId !== null && (
                        <Button color="inherit" onClick={logout}>Logout</Button>
                    )}

                    {authUserId === null && (
                        <>
                            <Button color="inherit" onClick={() => navigate("/login")}>Login</Button>
                            <Button color="inherit" onClick={() => navigate("/signup")}>Signup</Button>
                        </>
                    )}

                    <Button
                        sx={{ display: isLogin ? "inherit" : "none" }}
                        id="profilePic"
                        ref={profileIconRef}
                        onClick={() => setShowProfile(true)}
                    >
                        <img src={require('../../../resources/profile.png')} alt="profile" />
                    </Button>

                    <AccountMenu
                        username={username}
                        anchorEl={profileIconRef}
                        open={showProfile}
                        onClose={() => setShowProfile(false)}
                        logOutHandler={() => {
                            setAuthUserId(null);
                            setUsername(null);
                            setUserPerm(null);
                        }}
                    />
                    <Menu
                        anchorEl={anchorEl}
                        open={Boolean(anchorEl)}
                        onClose={handleMenuClose}
                        >             
                        <MenuItem onClick={() => { navigate("/home"); handleMenuClose(); }}>Home</MenuItem>
                        <MenuItem onClick={() => { navigate("/viewBooking"); handleMenuClose(); }}>View/Book Rooms</MenuItem>
                        <MenuItem onClick={() => { navigate("/cancelBooking"); handleMenuClose(); }}>View/Cancel Bookings</MenuItem>
                        <MenuItem onClick={() => { navigate("/bookingHistory"); handleMenuClose(); }}>Booking History</MenuItem>
                        <MenuItem onClick={() => { navigate("/editAccount"); handleMenuClose(); }}>Edit Account</MenuItem>
                      </Menu>
                </Toolbar>
            </AppBar>
        </Box>
    );
}

