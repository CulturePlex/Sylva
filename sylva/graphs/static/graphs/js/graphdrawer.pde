// Global parameters
int WIDTH = 1162;
int HEIGHT = 300;
int GRID_SPACING = 10;
float scale = 4;


class Node{
  boolean visible, selected;
  float posx, posy;
  float radius;
  float selectedExpansion = 1.5;
  boolean finalNode;
  String name;
  ArrayList<Relation> relations;

  Node(float x, float y, String n){
    posx = x;
    posy = y;
    name = n;
    visible = true;
    relations = new ArrayList<Relation>();
  }

  void drawMe(){
    if (visible){
      for(int i=0;i<relations.size();i++){
        if (relations.get(i).getNode().isVisible()){
          relations.get(i).drawMe();
        }
      }
      radius = _nodeRadius;
      stroke(#999999);
      fill(#8EC1DA);
      if (selected){
        ellipse(posx, posy, radius*2*selectedExpansion, radius*2*selectedExpansion);
      } else {
        ellipse(posx, posy, radius*2, radius*2);
      }
      fill(0);
      text(name, posx, posy);
      strokeWeight(1);
    }
  }

  boolean touchingMe(float x, float y){
    if (!visible) return false;
    if (selected){
      return (dist(posx, posy, x, y) < radius*selectedExpansion);
    } else {
      return (dist(posx, posy, x, y) < radius);
    }
  }

  String getName(){
    return name;
  }

  void setSelected(){
    selected=true;
  }

  void setUnselected(){
    selected=false;
  }

  void addRelation(Relation r){
    relations.add(r);
  }

  boolean isVisible(){
    return visible;
  }

  float getX(){
    return posx;
  }

  void setX(float x){
    posx=x;
  }

  float getY(){
    return posy;
  }

  void setY(float y){
    posy=y;
  }

  String[] getRelationshipTypes(){
    String[] buffer = {};
    for(int i=0;i<relations.size();i++){
      //TODO Remove repeated ones
      buffer = append(buffer, relations.get(i).getType());
    }
    return buffer;
  }

  boolean hasEdge(String type, String target){
    for(int i=0;i<relations.size();i++){
      if (relations.get(i).getType()==type && relations.get(i).getNode().getName()==target){
        return true;
      }
    }
    return false;
  }


  void setVisible(boolean b){
    visible=b;
  }

  Node getRelated(String n, String t){
    Relation r;
    for(int i=0;i<relations.size();i++){
      r = relations.get(i);
      if ((r.getType()==t) && (r.getNode().getName()==n)){
        return r.getNode();
      }
    }
    return null;
  }

  void setAsFinal(){
    finalNode=true;
  }

  boolean isFinal(){
    return finalNode;
  }

  ArrayList<Relation> getRelations(){
    return relations;
  }

  void removeRelation(String type, String target){
    ArrayList<Relation> temp = new ArrayList<Relation>();
    for(int i=0;i<relations.size();i++){
      if (type!=relations.get(i).getType() || target!=relations.get(i).getNode().getName()){
        temp.add(relations.get(i));
 //       temp = append(temp, (Relation)relations[i]);
      }
    }
    relations = temp;
  }
}

class Relation{
  String type;
  Node source;
  Node target;

  Relation(Node sNode, String t, Node tNode){
    source=sNode;
    type=t;
    target=tNode;
  }

  Node getNode(){
    return target;
  }

  String getType(){
    return type;
  }

  void drawMe(){
    stroke(#8EC1DA);
    line(source.getX(), source.getY(), target.getX(), target.getY());
    noStroke();
    fill(0);
    text(type, (source.getX()+target.getX())/2, (source.getY()+target.getY())/2);

  }
}


float _nodeRadius;
ArrayList<Node> _nodeList = new ArrayList<Node>();

Node getNode(String nodeName) {
  for(int i=0;i<_nodeList.size();i++){
    if (_nodeList.get(i).getName()==nodeName){
      return _nodeList.get(i);
    }
  }
  return null;
}

void draw_background(gridSpacing) {
  background(#FFFFFF);
  stroke(#EEEEEE);
  for(int i=0;i<width;i+=gridSpacing){
    line(i, 0, i, height);
  }
  for(int i=0;i<height;i+=gridSpacing){
    line(0, i, width, i);
  }
}

void setup() {
  float drawableWidth, drawableHeight;
  Node newNode;
  Relation newRelation;
  size(WIDTH,HEIGHT);
  smooth();
  stroke(0);
  noStroke();
  _nodeRadius = 20;
  PFont fontA = loadFont("Verdana");  
  textFont(fontA, 8);  
  textAlign(CENTER);
}


void draw(){
  draw_background(GRID_SPACING);

  _nodeRadius = width/(scale*_nodeList.size());

  if (mousePressed) {
    for(int i=0;i<_nodeList.size();i++){
      if (_nodeList.get(i).touchingMe(mouseX, mouseY)){
        unselectAll();
        _nodeList.get(i).setSelected();
        _nodeList.get(i).setX(mouseX);
        _nodeList.get(i).setY(mouseY);
        break;
      }
    }
  } else {
    unselectAll();
  }
  for(int i=0;i<_nodeList.size();i++){
    _nodeList.get(i).drawMe();
  }
}

void unselectAll(){
  for(int i=0;i<_nodeList.size();i++){
    _nodeList.get(i).setUnselected();
  }
}

void addNode(String nodeName){
  Node newNode;
  newNode = new Node(random(width), random(height), nodeName);
  _nodeList.add(newNode);
}

void addLocatedNode(String nodeName, float xpos, float ypos){
  Node newNode;
  float x = width*norm(xpos, -1400, 1400);
  float y = height*norm(ypos, -1000, 1400);
  newNode = new Node(x, y, nodeName);
  _nodeList.add(newNode);
}

void deleteNode(String nodeName){
  ArrayList<Node> tempList = new ArrayList<Node>();
  for(int i=0;i<_nodeList.size();i++){
    if (_nodeList.get(i).getName() != nodeName){
      tempList.add(_nodeList.get(i));
    }
  }
  _nodeList = tempList;
}

void addEdge(String source, String type, String target){
  Relation newRelation = new Relation(getNode(source), type, getNode(target));
  getNode(source).addRelation(newRelation);
}

void deleteEdge(String source, String type, String target){
  Node sourceNode = getNode(source);
  sourceNode.removeRelation(type, target);
}

void test(){
  addNode("Tolkien");
  addNode("LOTR");
  addNode("Sam");
  addNode("Frodo");
  addNode("Mount Doom");
  addEdge("Tolkien", "wrote", "LOTR");
  addEdge("Frodo", "appears_in", "LOTR");
  addEdge("Sam", "appears_in", "LOTR");
  addEdge("Frodo", "goes_to", "Mount Doom");
  addEdge("Sam", "goes_to", "Mount Doom");
  addNode("Bambi");
  addEdge("Bambi", "appears_in", "LOTR");
  deleteEdge("Bambi", "appears_in", "LOTR");
  deleteNode("Bambi");
}
