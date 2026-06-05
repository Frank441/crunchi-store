import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        primary: {
            main: '#5B80DC',
        },
        text: {
            primary: '#FFFFFF',
        }
    },
    components: {
        MuiTextField: {
            styleOverrides: {
                root: {
                    borderBottom: '2px solid #FFFFFF70',
                    '& .MuiInputBase-input': {
                        color: '#FFFFFF',
                    },
                    '& .MuiInputBase-input::placeholder': {
                        color: '#FFFFFF',
                        opacity: 0.7,
                    },
                },
            },
        },
        MuiFormLabel: {
            styleOverrides: {
                root: {
                    color: '#FFFFFF !important',
                    fontFamily: 'Ubuntu, sans-serif',
                },
            },
        },
    },
});

export default theme;