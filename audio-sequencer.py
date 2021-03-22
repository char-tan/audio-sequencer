# Package imports
import numpy  # numpy arrays are used to store and manipulate audio
# Throws the following error on the university linux pc OSError: PortAudio library not found
# Requires the install of the PortAudio library
import sounddevice  # Used to output audio
import soundfile  # used to save audio as wav file
import scipy.signal  # used to create numpy arrays for different wavetypes and for audio filtering
from scipy.io import wavfile  # used to create numpy array from wav file
from tkinter import *  # tkinter is the GUI manager
import itertools  # used to create toggle cycles
import os  # used to check file exists

# Relevant to external code
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # used to plot onto tkinter window
from matplotlib.figure import Figure  # used to plot

# Below lines of code are used to ignore a warning caused when reusing matplotlib figures
import warnings 
import matplotlib.cbook
matplotlib.use('TkAgg')
warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)


# Class and function arguments were not capitalised/CamelCase to help identify them/improve readability
# Global is used for certain variables because you cannot return to a widget callback/command

# This is a parent class for all buttons with a toggle cycle effect
class TogglingButtons:
    def __init__(self, window, row, column, colour1, colour2):
        # Creates the buttons
        self.TogglingButton = Button(window)
        # Puts the button on the grid at a specific location
        self.TogglingButton.grid(row=row, column=column)

        # Use itertools to create a cycle for the button toggle effect
        self.ReliefCycle = itertools.cycle(['sunken', 'raised'])
        self.ColourCycle = itertools.cycle([colour2, colour1])

    def Toggler(self):
        # Creates a toggle effect with change of colour by cycling through the itertools cycles
        self.TogglingButton['relief'] = str(next(self.ReliefCycle))
        self.TogglingButton['bg'] = str(next(self.ColourCycle))


# This is a subclass for buttons used to sequence drums
class DrumButtons(TogglingButtons):
    def __init__(self, window, row, column, colour1, colour2):
        # Calls the parent class, creating the button and allowing use of Toggler function
        super().__init__(window, row, column, colour1, colour2)
        # Reconfigures the button, lambda: [f() for f in] is used to have multiple commands for same button callback
        self.TogglingButton.config(height=2, width=6, bg=colour1,
                                   command=lambda: [f() for f in [self.AlterSequence, self.Toggler]])

        # Instance attributes for row and column needed for AlterSequence
        self.ButtonRow = row
        self.ButtonColumn = column

    def AlterSequence(self):
        global Sequencer  # Allows changes to be made to the variable globally
        # Multiplies the corresponding value in Sequencer by -1
        Sequencer[self.ButtonRow-2][self.ButtonColumn-1] *= -1


# This is a subclass for buttons used to select options
class OptionButtons(TogglingButtons):
    def __init__(self, window, row, column, colour1, colour2, option, text):
        # Calls the parent class, creating the button and allowing use of Toggler function
        super().__init__(window, row, column, colour1, colour2)
        # Reconfigures the button, lambda: [f() for f in] is used to have multiple commands for same button callback
        self.TogglingButton.config(bg=colour1, text=text, command=lambda: [f() for f in [self.AlterOption, self.Toggler]])

        # Instance attributes for option needed for AlterOption
        self.Option = option

    def AlterOption(self):
        global ButtonOptions # Allows changes to be made to the variable globally
        # Multiplies the corresponding value in ButtonOptions by -1
        ButtonOptions[self.Option] *= -1


# This is a subclass for buttons used to mute channels
class MuteButtons(TogglingButtons):
    def __init__(self, window, row, column, colour1, colour2):
        # Calls the parent class, creating the button and allowing use of Toggler function
        super().__init__(window, row, column, colour1, colour2)
        # Reconfigures the button, lambda: [f() for f in] is used to have multiple commands for same button callback
        self.TogglingButton.config(text='MUTE', bg=colour1, command=lambda: [f() for f in [self.AlterMute, self.Toggler]])

        # Instance attributes for row needed for AlterMute
        self.Row = row

    def AlterMute(self):
        # Multiplies the corresponding value in Sequencer by -1
            global MuteOptions
            MuteOptions[self.Row-2] *= -1


# This class is drop down lists used to write the musical notes
class NoteMenus:
    # Function initialises instances of the class
    def __init__(self, window, row, column):
        # Creates list of possible options for the drop down menu
        self.Options = ['X', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        self.Note = StringVar(window)  # Creates instance attribute Note
        self.Note.set("X")  # Sets Note to 'X' (default)
        # Creates drop down list with options from list above, starting on default of 'X'
        self.NoteMenu = OptionMenu(window, self.Note, *self.Options, command=self.AlterNote)
        self.NoteMenu.config(height=2, width=2)  # reconfigures widget size
        self.NoteMenu.grid(row=row, column=column)  # places drop down list on grid

        # Instance attributes for row and column needed for AlterNote
        self.MenuRow = row
        self.MenuColumn = column

    def AlterNote(self, value):
        global Sequencer  # Allows changes to be made to the variable globally
        # Assigns corresponding Sequencer value (at correct index) to the Note chosen by user
        Sequencer[self.MenuRow-2][self.MenuColumn-1] = value


# This class only used once but I decided to have most GUI widgets as classes to help with readability and consistency
class BPMEntryField:
    # Function initialises instances of the class
    def __init__(self, window, row, column):
        # Creates entry widget, when a character is entered ForceNumbers is called, this must return True for
        # character to be accepted
        # Contains external code (cited in report)
        self.EntryField = Entry(window, width=5, validate="key",
                                validatecommand=((window.register(self.ForceNumbers)), '%S'))
        self.EntryField.insert(0, 120)  # inserts default value into entry field
        self.EntryField.grid(row=row, column=column)  # places entry field on the grid

        # Create button widget which when pressed calls NumberEntry command
        self.EnterButton = Button(MasterWindow, bg='grey', text="Enter", width=10, command=self.NumberEntry)
        self.EnterButton.grid(row=row, column=column+1)  # places button on the grid

    def ForceNumbers(self, character):
        # Receives the characters entered and returns True only if numerical
        return character.isdigit()

    def NumberEntry(self):
        # Checks if entered value is within range
        if int(self.EntryField.get()) not in range(100, 181):
            # If not within range background changed to red and a error pop up appears
            self.EntryField.config(bg='red')
            ErrorPopUp = Toplevel()
            ErrorMessage = Message(ErrorPopUp, text='BPM out of supported rang'
                                                    'e\nPlease enter a value between 100 and 180')
            ErrorMessage.pack()
        else:
            # Else the value is within range
            global BPM
            # int and get() used to get integer value of entry, this is then assigned to BPM globally
            BPM = int(self.EntryField.get())
            self.EntryField.config(bg='white')  # returns background to white

# Class for all Scale widgets
class Sliders:
    # Function initialises instances of the class
    def __init__(self, window, row, column, start=1, stop=5, default=3, orientation=HORIZONTAL):
        # Creates Scale widget with parameters defined by class arguments
        self.Slider = Scale(window, from_=start, to=stop, orient=orientation, command=self.SliderAssign)
        self.Slider.set(default)  # Sets the default value
        self.Slider.grid(row=row, column=column)  # Places Slider on grid

        self.Row = row  # Instance attribute for row needed for SliderAssign function

    def SliderAssign(self, value):
        global SliderValues
        # Changes vlaue of SilderValues at correct index globally
        SliderValues[self.Row-2] = int(value)


class PlayPause: #shoould add argument or something for BPM
    # Function initialises instances of the class
    def __init__(self, window, bpm, playrow=0, playcolumn=19, pauserow=0, pausecolumn=20, saverow=0, savecolumn=0):
        # Creates buttons and text entry field
        self.PlayButton = Button(window, bg='green', text='PLAY', command=self.Play)
        self.PauseButton = Button(window, bg='red', text='PAUSE', command=self.Pause)
        self.SaveButton = Button(window, bg='orange', text='SAVE', command=self.Save)
        self.SaveEntry = Entry(window, width=10)
        self.SaveEntry.insert(0, 'filename') # assings default text to entry

        # Puts the widgets on the grid
        self.PlayButton.grid(row=playrow, column=playcolumn)
        self.PauseButton.grid(row=pauserow, column=pausecolumn)
        self.SaveButton.grid(row=saverow+1, column=savecolumn)
        self.SaveEntry.grid(row=saverow, column=savecolumn)

        # instance attribute for window needed for PlotAudio function
        self.Window = window

        # Class attributes used in both plotting and generation of audio defined
        PlayPause.SampleRate = 44100
        PlayPause.Duration = (60 / bpm) / 4  # calculates the duration of the 1/4 beat in seconds
        PlayPause.BeatLength = int(PlayPause.Duration * PlayPause.SampleRate)  # as above in samples

        # Creates numpy array for time axis used in plotting
        PlayPause.TimeAxis = numpy.arange(PlayPause.BeatLength * 16)
        # Creates numpy zero array with length of full loop
        PlayPause.SilentChannel = numpy.zeros(PlayPause.BeatLength * 16)

        # Creates a figure to be used in plotting, this is in the __init__ function so a blank plot appears at start
        PlayPause.PlotFigure = Figure(figsize=(11, 2))
        # Adds subplot
        PlayPause.AudioPlot = PlayPause.PlotFigure.add_subplot(111)
        self.PlotAudio(PlayPause.SilentChannel) # plots a blank audio file on the figure

    # Envelopes are used in this program to fade in, fade out and to shorten the length of the sounds
    # In order to calculate the product of 2 numpy arrays they must be the same length so care was taken to ensure
    # there were no errors caused by rounding
    def EnvelopeGenerator(self, attack, release, silence, beatlength):
        # numpy array  with values 0 to 1 with length of attack (fade in)
        AttackArray = numpy.linspace(0, 1, num=int(attack))
        # numpy array with values 0 to 1 with length of release (flipped horizontally for fade out)
        ReleaseArray = numpy.flip(numpy.linspace(0, 1, num=int(release)))
        # numpy.full array with length beatlength-attack-release-silence, fill value 1 (max amplitude for sustain)
        SustainArray = numpy.full((int(beatlength) - int(attack) - int(release) - int(silence)), 1)
        # numpy.zero array with length of silence (zero amplitude for silence)
        SilenceArray = numpy.zeros(int(silence))

        # stacks the above arrays into a single array
        EnvelopeArray = numpy.hstack((AttackArray, SustainArray, ReleaseArray, SilenceArray))
        return EnvelopeArray

    # Function makes loop from the desired sequence
    def LoopGenerator(self, sequence, sounddata, silentbeat):
        LoopSequence = []  # creates empty list
        for Beat in sequence:  # iterates through the sequence (list)
            if Beat == 1:  # a 1 indicates the user has chosen a drum sound to be in this beat
                LoopSequence.append(sounddata)  # appends the sound as numpy array to the LoopSequence list
            elif type(Beat) == str and Beat != 'X': # a string other than 'X' indicates a musical note
                LoopSequence.append(sounddata[Beat])  #appends the corresponding numpy array
            else:  # the list value is -1 and the user has not chosen for the sound to be in this beat
                LoopSequence.append(silentbeat)  # appends the zero numpy array to the LoopSequence list
        # LoopSequence is now a list of numpy arrays
        Loop = numpy.concatenate(LoopSequence)  # concatenates the list into a single numpy array
        return Loop

    # Function to synthesise melodic elements, the code is designed to reduce the processing required
    # because only the notes needed are generated and if notes are repeated the same numpy array is reused
    def SynthDataGenerator(self, sequence, envelope, notefrequencies, beatlength, attackfilter):
        SynthData = {}  # will be dictionary with format {Note:numpy array of Note audio}
        SynthNotes = list(set(sequence))  # list(set()) was used to remove duplicate notes
        SynthNotes.remove('X')
        for Note in SynthNotes:
            # uses scipy.signal.square to produce a squarewave with frequency of musical note
            SynthData[Note] = scipy.signal.square(2 * numpy.pi * notefrequencies[Note]
                                                  * numpy.arange(beatlength) / PlayPause.SampleRate)
            if attackfilter == 1:  # user has selected the attack filter option
                SynthData[Note] = self.AttackFilter(SynthData[Note])  # calls AttackFilter function
            SynthData[Note] *= envelope  # calculates product of audio with envelope
        return (SynthData)

    # Function applies an enveloped filter to provided audio (the cutoff frequency increases with time)
    # This was a stretch goal and sounds a little rough due to artifacts created in the process but was interesting
    # to code. scipy.signal.butter was used to create filter arrays and these were then applied to the audio
    def AttackFilter(self, audio):
        # The number of samples each filter (with unique cutoff freq) will be applied to
        StepSize = 91
        Steps = int(len(audio) / StepSize)  # the number of whole steps that fit in the length of the audio file
        PreFilter = scipy.signal.butter(10, 250, fs=44100, output='sos')  # cutoff of 250 before main filter
        Audio = scipy.signal.sosfilt(PreFilter, audio)  # applies the PreFilter to audio
        # Creates an array with equal step size from 200 to 2500
        EnvelopeArray = numpy.linspace(200, 2500, num=Steps + 1)
        # This will be a list of numpy arrays containing audio, each with a filter of different cutoff frequency applied
        FilteredList = []
        for k in range(0, Steps + 1):  # iterates through the number of steps+1 to account for the remainder of division
            Filter = (scipy.signal.butter(10, EnvelopeArray[k], fs=44100, output='sos'))
            if k != Steps:
                # Applies Filter to the corresponding slice of Audio
                FilteredList.append(scipy.signal.sosfilt(Filter, Audio[StepSize * k:StepSize * (k + 1)]))
            else:
                # Applies Filter to the remaining samples of Audio (remainder of division)
                FilteredList.append((scipy.signal.sosfilt(Filter, Audio[StepSize * k:])))
        Audio = numpy.hstack(FilteredList)  # horizontally stacks the list of numpy arrays into a single array

        # PostFilter is used to low pass the audio a final time to remove some of the roughness I believe is caused
        # by digital artifacts from the above process
        PostFilter = scipy.signal.butter(10, 10000, fs=44100, output='sos')
        Audio = scipy.signal.sosfilt(PostFilter, Audio)
        return Audio

    def MakeMusic(self, beatlength, silentchannel):
        SilentBeat = numpy.zeros(beatlength)  # Creates numpy zero array with length of 1/4 beat in samples
        SoundDictionary = dict.fromkeys(['Kick', 'Snare', 'OpenHat', 'ClosedHat', 'LowSynth', 'TopSynth'])

        #  Generation or import of drum sound data

        # Kick drum
        # Uses scipy.signal.chirp to create a sine wave with logarithmic decreasing frequency
        # range determined by KickOption
        # KickData is the product of this chirp with the KickEnvelope (Envelope used to fade in/out and reduce popping)
        KickTimeArray = numpy.linspace(0, 0.125, num=beatlength)  # Creates numpy array with linspace
        KickOption = SliderValues[0]  # determined by user with slider (changes deepness of kick)
        KickEnvelope = self.EnvelopeGenerator(100, 900, 0, beatlength)  # calls EnvelopeGenerator
        SoundDictionary['Kick'] = KickEnvelope * scipy.signal.chirp(KickTimeArray, f0=200 + KickOption * 10,
                                                                    f1=55, t1=(0.04 + KickOption * 0.02),
                                                                    method='logarithmic')

        # Snare drum, attempted generation but was unsuccessful so uses imported WAV file
        # Assigns audio file to SnareFile
        SampleRateWav, SnareFile = wavfile.read(SnareLocation)
        SnareOption = 6 - SliderValues[1]  # determined by user with slider (changes length of snare)
        # Calls EnvelopeGenerator with the SnareOption determining the length of silence in the envelope
        SnareEnvelope = self.EnvelopeGenerator(0, 200, SnareOption * beatlength / 8, beatlength)
        # SnareData is product of SnareFile with length BeatLength and SnareEnvelope
        # SnareFile is sliced because it is longer than any possible BeatLength
        SoundDictionary['Snare'] = SnareEnvelope * 0.00003 * SnareFile[0:beatlength]

        # HiHats, use numpy.random.normal to produce white noise
        # Open/ClosedHatData are the product of this with the gain and respective envelopes
        OpenHatOption = SliderValues[2]  # determined by user with slider (changes release/fade out of hat)
        # Calls EnvelopeGenerator with the OpenHatOption determining the length of release
        OpenHatEnvelope = self.EnvelopeGenerator(30, beatlength * OpenHatOption / 6, 0, beatlength)
        SoundDictionary['OpenHat'] = OpenHatEnvelope * 0.07 * (numpy.random.normal(loc=0.0, scale=1.0, size=beatlength))

        ClosedHatOption = 5 - SliderValues[3]  # determined by user with slider (changes length of hat)
        # Calls EnvelopeGenerator with the ClosedHatOption determining the length of silence in the envelope
        ClosedHatEnvelope = self.EnvelopeGenerator(30, beatlength / 8, beatlength * ClosedHatOption / 6, beatlength)
        SoundDictionary['ClosedHat'] = ClosedHatEnvelope * 0.07 * (numpy.random.normal
                                                                   (loc=0.0, scale=1.0, size=beatlength))

        # Synthesisers

        LowSynthOption = SliderValues[4] - 1  # determined by user with slider (changes attack/fade in of synth)
        # Calls EnvelopeGenerator function with attack time determined by LowSynthOption
        LowSynthEnvelope = self.EnvelopeGenerator(LowSynthOption * beatlength / 6 + beatlength / 10, beatlength / 10, 0,
                                             beatlength) * 0.2
        SoundDictionary['LowSynth'] = self.SynthDataGenerator(Sequencer[4], LowSynthEnvelope, NoteFrequencies, beatlength,
                                                         ButtonOptions['LowFilter'])

        TopSynthEnvelope = self.EnvelopeGenerator(300, 300, 0, beatlength) * 0.2
        SoundDictionary['TopSynth'] = self.SynthDataGenerator(Sequencer[5], TopSynthEnvelope,
                                                              NoteFrequencies, beatlength, 2)

        # LoopGenerator is called to create a full 16x 1/4 beat loop for each channel
        # Use the index on Sequencer to get the corresponding nested list, and provide correct sound data as argument

        LoopDictionary = {}
        Counter = 0
        for Sound in SoundDictionary:
            global MuteOptions
            if MuteOptions[Counter] == 1:
                LoopDictionary[Sound] = silentchannel
            else:
                LoopDictionary[Sound] = self.LoopGenerator(Sequencer[Counter], SoundDictionary[Sound], SilentBeat)
            Counter += 1

        # Below code is used to apply the low pass filter to the top synth if necessary
        TopSynthOption = SliderValues[5] - 1
        if ButtonOptions['HighFilter'] == 1:
            FilterFreqs = [500, 2000, 6000, 10000, 16000]
            # scipy.signal.butter used for butterworth filter
            TopSynthFilter = scipy.signal.butter(10, FilterFreqs[TopSynthOption], fs=44100, output='sos')
            # Applies the filter to the TopSynth loop
            LoopDictionary['TopSynth'] = scipy.signal.sosfilt(TopSynthFilter, LoopDictionary['TopSynth'])

        # Applies master gain to full loop
        MasterGain = SliderValues[6] / 100
        FullLoop = sum(LoopDictionary.values()) * MasterGain

        return FullLoop

    # Function plots audio waveform on tkinter GUI
    def PlotAudio(self, audio):
        PlayPause.AudioPlot.cla()  # clears the figure ready for new plot
        PlayPause.TimeAxis = numpy.arange(PlayPause.BeatLength * 16)  # creates new time axis in case BPM has changed
        PlayPause.AudioPlot.plot(PlayPause.TimeAxis, audio, color='blue')  # plots the numpy array audio
        PlayPause.AudioPlot.axis('off')  # removes the axis
        # Throws a UserWarning that I have been unable to supress, other users online seem to have same issue
        PlayPause.PlotFigure.tight_layout()  # reduces the border around the plot

        # Contains external code, cited in report
        Canvas = FigureCanvasTkAgg(PlayPause.PlotFigure, master=self.Window) # prepares the figure for placement on the grid
        Canvas.get_tk_widget().grid(row=0, column=1, rowspan=2, columnspan=16) # positions the figure on the grid
        Canvas.draw()

    # Function generates audio and then starts playback
    def Play(self):
        PlayPause.Duration = (60 / BPM) / 4  # calculates the duration of the 1/4 beat in seconds
        PlayPause.BeatLength = int(PlayPause.Duration * PlayPause.SampleRate)  # as above in samples
        PlayPause.SilentChannel = numpy.zeros(PlayPause.BeatLength * 16)  # SilentChannel recalculated in case new BPM
        PlayPause.Music = self.MakeMusic(PlayPause.BeatLength, PlayPause.SilentChannel) # calls MakeMusic function
        self.PlotAudio(PlayPause.Music) # calls PlotAudio function to update the figure
        sounddevice.play(PlayPause.Music, 44100, loop=True) # uses sound device to playback numpy array, looping

    # Function stops audio playback
    def Pause(self):
        sounddevice.stop()

    # Function saves current audio as wav file with name from entryfield
    def Save(self):
        soundfile.write(self.SaveEntry.get()+'.wav', PlayPause.Music, 44100)

# Class for GUI labels
class Labels:
    def __init__(self, window, row, column, text):
        self.TextLabel = Label(window, text=text)
        self.TextLabel.grid(row=row, column=column)

print('Welcome to the Drum Machine/Synthesier/Sequencer\nInformation on using this program can be found in the'
      ' attached report\nHeadphones are recommended, I hope you enjoy!\n')

# Dictionary with format {Note:Frequency(Hz)}
NoteFrequencies = {'A': 55, 'A#': 58.27, 'B': 61.74, 'C': 65.41, 'C#': 69.3, 'D': 73.42, 'D#': 77.78,
                   'E': 82.41, 'F': 87.31, 'F#': 92.5, 'G': 98, 'G#': 103.83}

# Entry of location of snare drum file for import, with error checking
SnareLocation = r'C:\Users\Charlie\Documents\Snare.wav'
# While loop repeats until file ends with .wav and exists
while not SnareLocation.endswith('.wav') or not os.path.isfile(SnareLocation):
    print("Invalid file type/location, only compatible with .wav files")
    SnareLocation = input('Please enter a valid file location: ')

# Default values are set
BPM = 120  # used with global in the NumberEntry function of BPMEntryField class
SliderValues = [3] * 6 + [100]  # used with global in the SliderAssign function of Slider class
# Sequencer will be a nested list with each sublist corresponding to the pattern of an audio channel
Sequencer = []  # used with global in the classes
MuteOptions = [-1]*6  # used with global in the classes
ButtonOptions = {'LowFilter': -1, 'HighFilter': -1}  # used with global in the classes

# Creates main/root window for GUI elements
MasterWindow = Tk()

# The below nested for loops are used to iterate over the range of rows and columns needed

WidgetList = []  # widget list will be a list full of class instances, used to iterate over range of rows and columns
for i in range(2, 6):  # iterates 4 times (4 rows)
    # Appends a list with -1 16 times to sequencer, -1 is default value and corresponds to a silent/dead beat
    Sequencer.append([-1] * 16)
    for j in range(1, 17):  # iterates 16 times (16 columns)
        if j in [1, 5, 9, 13]:  # causes the drum buttons on the downbeats to be a different colour
            Colour1 = 'PaleGreen3'
            Colour2 = 'Green3'
        else:
            Colour1 = 'LightSkyBlue2'
            Colour2 = 'DeepSkyBlue3'
        # Creates an instance of DrumButtons on each iteration
        WidgetList.append(DrumButtons(MasterWindow, i, j, Colour1, Colour2))


for i in range(6, 8):  # iterates 2 times (2 rows)
    # Appends a list with 'X' 16 times to sequencer, 'X' is default value and corresponds to a silent/dead beat
    Sequencer.append(['X'] * 16)
    for j in range(1, 17):  # iterates 16 times (16 columns)
        # Creates an instance of NoteMenus on each iteration
        WidgetList.append(NoteMenus(MasterWindow, i, j))

WidgetList.append(BPMEntryField(MasterWindow, 1, 19)) # creates instance of BPMEntryField

for i in range(2, 8):  # iterates 6 times
    # Creates an instance of MuteButtons and Sliders on each iteration
    WidgetList.append(MuteButtons(MasterWindow, i, 20, 'grey', 'red'))
    WidgetList.append(Sliders(MasterWindow, i, 18))
# Creates instance of slider with different parameters for master gain
WidgetList.append(Sliders(MasterWindow, 1, 17, 100, 0, 100, 'vertical'))

# Creates instances of OptionButtons class
LowSynthButton = OptionButtons(MasterWindow, 6, 19, 'grey', 'red', 'LowFilter', 'Attack Filter')
HighSynthButton = OptionButtons(MasterWindow, 7, 19, 'grey', 'red', 'HighFilter', 'Filter')

# Creates instance of PlayPause class
PlayPauseButtons = PlayPause(MasterWindow, BPM)

# Used to label all channels without individual lines of code
Counter = 2  # offsets the row by 2
for Channel in ['Kick', 'Snare', 'Open HiHat', 'Closed HiHat', 'Low Synth', 'Top Synth']:
    WidgetList.append(Labels(MasterWindow, Counter, 0, Channel))
    Counter += 1

# Below labels all had different text so had to be added with individual lines of code
WidgetList.append(Labels(MasterWindow, 2, 17, 'Deepness'))
WidgetList.append(Labels(MasterWindow, 3, 17, 'Length'))
WidgetList.append(Labels(MasterWindow, 4, 17, 'Decay'))
WidgetList.append(Labels(MasterWindow, 5, 17, 'Length'))
WidgetList.append(Labels(MasterWindow, 6, 17, 'Attack'))
WidgetList.append(Labels(MasterWindow, 7, 17, 'Filter Cutoff'))
WidgetList.append(Labels(MasterWindow, 0, 17, 'Master'))
WidgetList.append(Labels(MasterWindow, 1, 18, 'BPM'))

MasterWindow.mainloop()  # Maintains the GUI window until it is closed