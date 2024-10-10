import React from "react";
import PropTypes from "prop-types";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";

const AIAssistantSummary = ({ config, aiProfile, open, onClose }) => {
  if (!aiProfile) {
    return null; // Don't render anything if aiProfile is null
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>AI Assistant Summary</DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} style={{ padding: "1rem" }}>
              <Typography variant="h6" gutterBottom>
                Configuration
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Base Model"
                    secondary={config.baseModel}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Personality"
                    secondary={config.personality}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Primary Expertise"
                    secondary={config.primaryExpertise}
                  />
                </ListItem>
                {/* Add more configuration details as needed */}
              </List>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} style={{ padding: "1rem" }}>
              <Typography variant="h6" gutterBottom>
                AI Profile
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Always On"
                    secondary={aiProfile.always_on ? "Yes" : "No"}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Base Model"
                    secondary={aiProfile.base_model}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Communication Style"
                    secondary={aiProfile.communication_style}
                  />
                </ListItem>
                {/* Add more AI profile details as needed */}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

AIAssistantSummary.propTypes = {
  config: PropTypes.object.isRequired,
  aiProfile: PropTypes.object,
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default AIAssistantSummary;
